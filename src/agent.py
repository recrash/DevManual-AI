import os
from dotenv import load_dotenv
from typing import TypedDict, Literal
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import FAISS
# 저장된 프롬프트
from .prompts import rag_prompt
from .prompts import router_prompt


class AgentState(TypedDict):
    question: str # 사용자의 원본 질문
    route: Literal["rag_query", "code_generation", "ambiguous"] # 라우터가 결정한 경로
    answer: str  # RAG 노드가 생성한 답변을 저장할 공간

def router(state: AgentState):
    """
    사용자의 질문을 분석하여 다음 경로를 결정한다.
    """

    print("---라우터 노드 실행---")
    question = state["question"]

    # LLM 및 출력 파서 설정
    llm = AzureChatOpenAI(
        azure_endpoint=os.getenv("AOAI_ENDPOINT"),
        api_key=os.getenv("AOAI_API_KEY"),
        azure_deployment=os.getenv("AOAI_DEPLOY_GPT4O_MINI"),
        api_version="2024-02-01",
        temperature=0
    )
    
    # 프롬프트에서 요구한 대로 JSON으로 리턴받은 결과값을 파싱
    parser = JsonOutputParser()

    router_chain = router_prompt | llm | parser
    response = router_chain.invoke({"question": question})

    # 결정된 경로를 상태(State)에 저장
    print(f"결정된 경로: {response['route']}")
    state["route"] = response["route"]

    return state

def rag_node(state: AgentState):
    """
    문서 저장소를 기반으로 질문에 대한 답변을 생성한다.
    """

    print("---RAG 노드 실행---")
    question = state["question"]

    # Retriever 로드
    embeddings = AzureOpenAIEmbeddings(
        azure_endpoint=os.getenv("AOAI_ENDPOINT"),
        api_key=os.getenv("AOAI_API_KEY"),
        azure_deployment=os.getenv("AOAI_DEPLOY_EMBED_3_SMALL"),
        api_version="2024-02-01",
    )
    db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    retriever = db.as_retriever()

    # LLM 설정
    llm = AzureChatOpenAI(
        azure_endpoint=os.getenv("AOAI_ENDPOINT"),
        api_key=os.getenv("AOAI_API_KEY"),
        azure_deployment=os.getenv("AOAI_DEPLOY_GPT4O_MINI"),
        api_version="2024-02-01",
        temperature=0.7
    )

    # Rag 체인 구성 및 실행
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | rag_prompt
        | llm
        | StrOutputParser()
    )

    answer = rag_chain.invoke(question)

    # 생성된 답변을 상태(State)에 저장
    state["answer"] = answer

    return state

def decide_next_node(state: AgentState):
    """
    라우터의 결정에 따라 다음 노드를 선택한다.
    """
    print("---다음 노드 결정---")
    if state["route"] == "rag_query":
        print("경로: RAG")
        return "rag_node"
    else:
        print("경로: 종료")
        return END



load_dotenv(dotenv_path="../.env")

# 그래프 정의
# 그래프 생성 후 어떤 State를 사용할지 알려준다
workflow = StateGraph(AgentState)

# 노드를 그래프에 추가
workflow.add_node("router", router)
workflow.add_node("rag_node", rag_node)

# 그래프의 시작점을 "router" 노드로 설정한다.
workflow.set_entry_point("router")

workflow.add_conditional_edges(
    "router",
    decide_next_node,
    {
        "rag_node": "rag_node",
        END: END
    }
)

workflow.add_edge("rag_node", END)

# 그래프를 실행 가능한 앱으로 컴파일한다.
app = workflow.compile()

if __name__ == "__main__":
    inputs = {"question": "LangGraph의 State가 뭐야?"}
    final_state = app.invoke(inputs)
    
    print("\n---최종 상태---")
    # final_state 딕셔너리에서 'answer' 키의 값을 예쁘게 출력
    print(final_state.get('answer', '답변이 생성되지 않았습니다.'))