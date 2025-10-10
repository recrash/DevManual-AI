import os
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import Tool
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from .prompts import rag_prompt, code_gen_prompt

# --- LLM 및 임베딩 모델 초기화 (도구 내부에서 사용할 모델) ---
# 도구들이 공통적으로 사용할 LLM과 임베딩 모델을 미리 정의합니다.
llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AOAI_ENDPOINT"),
    api_key=os.getenv("AOAI_API_KEY"),
    azure_deployment=os.getenv("AOAI_DEPLOY_GPT4O_MINI"),
    api_version="2024-02-01",
    temperature=0
)

embeddings = AzureOpenAIEmbeddings(
    azure_endpoint=os.getenv("AOAI_ENDPOINT"),
    api_key=os.getenv("AOAI_API_KEY"),
    azure_deployment=os.getenv("AOAI_DEPLOY_EMBED_3_SMALL"),
    api_version="2024-02-01",
)

# --- 1. 웹 검색 도구 ---
# 웹 검색 도구
search_tool = DuckDuckGoSearchRun()

# --- 2. RAG 검색 도구 ---

# RAG 체인 로직을 함수로 정의합니다.
def rag_chain(question: str):
    db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    retriever = db.as_retriever()
    
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | rag_prompt
        | llm
        | StrOutputParser()
    )
    return chain.invoke(question)

# --- 3. 코드 생성 도구 ---
# 코드 생성 체인 로직을 함수로 정의합니다.
def code_generation_chain(question: str):
    # 코드 생성 시에는 RAG 검색을 통해 관련성 높은 컨텍스트를 함께 제공합니다.
    db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    retriever = db.as_retriever(search_kwargs={'k': 5})
    retrieved_docs = retriever.invoke(question)
    context_text = "\n\n".join([doc.page_content for doc in retrieved_docs])
    
    # 토픽은 질문에서 LLM이 추론하도록 단순화합니다.
    chain = code_gen_prompt | llm | StrOutputParser()
    return chain.invoke({
        "question": question,
        "context": context_text,
        "topic": "사용자의 질문에 명시된 주제" # 감독관이 토픽을 직접 넘겨주지 않으므로 일반화
    })

# RAG 체인의 Tool화
rag_tool = Tool(
    name="rag_search",
    func=rag_chain,
    description="기술 문서, 소스 코드 등 로컬 파일 기반의 지식에 대해 답변할 때 사용합니다. LangChain, LangGraph 같은 특정 기술의 개념이나 사용법을 질문 받았을 때 가장 먼저 사용해야 하는 도구입니다."
)


# 코드 생성 체인 Tool화
code_gen_tool = Tool(
    name="code_generator",
    func=code_generation_chain,
    description="사용자로부터 특정 기능을 수행하는 소스 코드나 마크다운, JSON 등 특정 형식의 문서를 생성해달라는 요청을 받았을 때 사용합니다. '만들어줘', '짜줘', '작성해줘' 같은 키워드가 포함된 경우 유용합니다."
)