import os
from dotenv import load_dotenv
from typing import TypedDict, Literal, Optional
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import FAISS
from langchain.agents import create_tool_calling_agent, AgentExecutor

# 저장된 프롬프트
from .prompts import rag_prompt, router_prompt, code_gen_prompt, react_agent_prompt
# 인터넷 검색용
from .tools import search_tool


class AgentState(TypedDict):
    question: str # 사용자의 원본 질문
    route: Literal["rag_query", "code_generation", "unsupported"] # 라우터가 결정한 경로
    topic: Optional[str] # 라우터가 식별한 기술 토픽 (e.g., "LangGraph", "Spring Boot")
    answer: str  # RAG 노드가 생성한 답변을 저장할 공간

def router(state: AgentState):
    """
    사용자의 질문을 분석하여 다음 경로를 결정한다.
    """

    print("---라우터 노드 실행 (RAG 기반) ---")
    question = state["question"]

    # 1. RAG Retriever 로드 및 컨텍스트 검색
    print("FAISS에서 관련 문서 검색 중...")
    embeddings = AzureOpenAIEmbeddings(
        azure_endpoint=os.getenv("AOAI_ENDPOINT"),
        api_key=os.getenv("AOAI_API_KEY"),
        azure_deployment=os.getenv("AOAI_DEPLOY_EMBED_3_SMALL"),
        api_version="2024-02-01",
    )
    db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    retriever = db.as_retriever(search_kwargs={'k': 3}) # 관련 문서 3개만 가져오도록 설정

    retrieved_docs = retriever.invoke(question)
    # 검색된 문서 내용을 하나의 문자열로 합치기
    context_text = "\n\n".join([doc.page_content for doc in retrieved_docs])
    print("문서 검색 완료.")


    # 2. LLM 및 출력 파서 설정
    llm = AzureChatOpenAI(
        azure_endpoint=os.getenv("AOAI_ENDPOINT"),
        api_key=os.getenv("AOAI_API_KEY"),
        azure_deployment=os.getenv("AOAI_DEPLOY_GPT4O_MINI"),
        api_version="2024-02-01",
        temperature=0
    )
    
    # 프롬프트에서 요구한 대로 JSON으로 리턴받은 결과값을 파싱
    parser = JsonOutputParser()

    # 3. 새로운 라우터 프롬프트 체인 실행 (컨텍스트 포함)
    router_chain = router_prompt | llm | parser
    response = router_chain.invoke({
        "question": question,
        "context": context_text
    })

     # 4. 결정된 경로와 토픽을 상태(State)에 저장
    route = response.get("route", "unsupported")
    topic = response.get("topic")
    print(f"결정된 경로: {route}, 토픽: {topic}")

    state["route"] = route
    state["topic"] = topic

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
    route = state.get("route")
    
    if route == "rag_query":
        print("경로: RAG")
        return "rag_node"
    elif route == "code_generation":
        print("경로: code_generation")
        return "code_generation_node"
    else: # "unsupported 인 경우"
        print("경로: 종료(지원하지 않는 질문")
        return END

def code_generation_node(state: AgentState):
    """
    식별된 토픽(topic)과 관련 문서(context)를 기반으로 코드를 생성한다
    """
    print("---코드 생성 노드 실행---")
    question = state["question"]
    topic = state["topic"]

    # 1. 코드 생성에 더 깊은 컨텍스트를 제공하기 위해 RAG를 다시 실행
    print(f"'{topic}' 토픽에 대한 코드 생성을 위해 문서 검색 중...")
    embeddings = AzureOpenAIEmbeddings(
        azure_endpoint=os.getenv("AOAI_ENDPOINT"),
        api_key=os.getenv("AOAI_API_KEY"),
        azure_deployment=os.getenv("AOAI_DEPLOY_EMBED_3_SMALL"),
        api_version="2024-02-01",
    )
    db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    retriever = db.as_retriever(search_kwargs={'k': 5}) # 코드 생성을 위해 문서를 5개 참조

    retrieved_docs = retriever.invoke(question)
    context_text = "\n\n".join([doc.page_content for doc in retrieved_docs])
    print("문서 검색 완료.")

    # 2. LLM 설정
    llm = AzureChatOpenAI(
        azure_endpoint=os.getenv("AOAI_ENDPOINT"),
        api_key=os.getenv("AOAI_API_KEY"),
        azure_deployment=os.getenv("AOAI_DEPLOY_GPT4O_MINI"),
        api_version="2024-02-01",
        temperature=0.1 # 코드 생성 시에는 약간의 창의성보다 일관성이 중요하므로 온도를 낮게 설정
    )

    # 3. 코드 생성 프롬프트 체인
    code_gen_chain = code_gen_prompt | llm | StrOutputParser()

    answer = code_gen_chain.invoke({
        "question": question,
        "topic": topic,
        "context": context_text
    })

    state["answer"] = answer

    return state



# 실행 부분
load_dotenv(dotenv_path="../.env")

# 그래프 정의
# 그래프 생성 후 어떤 State를 사용할지 알려준다
workflow = StateGraph(AgentState)

# 노드를 그래프에 추가
workflow.add_node("router", router)
workflow.add_node("rag_node", rag_node)
workflow.add_node("code_generation_node", code_generation_node)

# 그래프의 시작점을 "router" 노드로 설정한다.
workflow.set_entry_point("router")

workflow.add_conditional_edges(
    "router",
    decide_next_node,
    {
        "rag_node": "rag_node",
        "code_generation_node": "code_generation_node",
        END: END
    }
)

workflow.add_edge("rag_node", END)
workflow.add_edge("code_generation_node", END) # 새로 추가한 엣지

# 그래프를 실행 가능한 앱으로 컴파일한다.
app = workflow.compile()


# ReAct용 인터넷 검색 툴
tools = [search_tool]

# ReAct 에이전트의 llm 설정
# 기존에 사용하던 gpt-4o-mini 모델을 그대로 사용
llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AOAI_ENDPOINT"),
    api_key=os.getenv("AOAI_API_KEY"),
    azure_deployment=os.getenv("AOAI_DEPLOY_GPT4O_MINI"),
    api_version="2024-02-01",
    temperature=0
)

# 프롬프트, LLM, 도구를 하나로 묶어 ReAct 에이전트를 생성
react_agent = create_tool_calling_agent(llm, tools, react_agent_prompt)

# 생성된 에이전트와 도구를 바탕으로 실행기 생성
react_agent_executor = AgentExecutor(agent=react_agent, tools=tools, verbose=True)

# agent.py 테스트용
if __name__ == "__main__":
    # ReAct 에이전트가 웹 검색을 잘 하는지 테스트해보자!
    question = {"input": "LangChain의 최신 버전은 뭐야?"}
    
    print("\n--- ReAct 에이전트 테스트 시작 ---")
    response = react_agent_executor.invoke(question)
    
    print("\n--- 최종 답변 ---")
    print(response.get('output', '답변이 생성되지 않았습니다.'))