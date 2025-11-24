import os
os.environ['GRPC_DNS_RESOLVER'] = 'native'
from dotenv import load_dotenv
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from .prompts import rag_prompt, code_gen_prompt

# .env 파일 로드
load_dotenv()

# --- LLM 및 임베딩 모델 초기화 (도구 내부에서 사용할 모델) ---
# 도구들이 공통적으로 사용할 LLM과 임베딩 모델을 미리 정의합니다.
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)

ragEmbeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    task_type="RETRIEVAL_QUERY"
)

codeGenEmbeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    task_type="RETRIEVAL_QUERY"
)

# --- 1. 웹 검색 도구 ---
# 웹 검색 도구
search_tool = DuckDuckGoSearchRun()

# --- 2. RAG 검색 도구 ---

# RAG 체인 로직을 함수로 정의합니다.
def rag_chain(question: str):
    db = FAISS.load_local("faiss_index", ragEmbeddings, allow_dangerous_deserialization=True)
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
    db = FAISS.load_local("faiss_index", codeGenEmbeddings, allow_dangerous_deserialization=True)
    retriever = db.as_retriever(search_kwargs={'k': 5})
    retrieved_docs = retriever.invoke(question)
    context_text = "\n\n".join([doc.page_content for doc in retrieved_docs])
    
    # 토픽은 질문에서 LLM이 추론하도록 단순화합니다.
    chain = code_gen_prompt | llm | StrOutputParser()
    return chain.invoke({
        "question": question,
        "context": context_text
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
    description="사용자가 예제 코드 작성, 특정 기능 구현, 소스 코드 생성 등을 요청할 때 **반드시** 사용해야 하는 도구입니다. 직접 코드를 작성하지 말고 이 도구를 호출하세요."
)