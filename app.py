import os
import streamlit as st
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# .env 로드
load_dotenv()


# 벡터DB 로드
def load_retriever():
    embeddings = AzureOpenAIEmbeddings(
        azure_endpoint=os.getenv("AOAI_ENDPOINT"),
        api_key=os.getenv("AOAI_API_KEY"),
        azure_deployment=os.getenv("AOAI_DEPLOY_EMBED_3_SMALL"),
        api_version="2024-02-01",
    )

    #faiss_index 지정
    db = FAISS.load_local("scripts/faiss_index", embeddings, allow_dangerous_deserialization=True)

    return db.as_retriever()


# LLM에게 RAG 수행을 지시하는 프롬프트 템플릿 정의
def get_rag_prompt():
    template = """
    너는 사용자의 기술 질문에 대해 친절하고 명확하게 답변해주는 AI 어시스턴트 'DevManual-AI'야.
    제시된 [Context] 정보를 바탕으로, 사용자의 [Question]에 대해 답변해줘.

    [Context]:
    {context}

    [Question]:
    {question}
    """
    return ChatPromptTemplate.from_template(template)

# Streamlit Settings
st.set_page_config(page_title="DevManual-AI", page_icon="🤖")
st.title("🤖 DevManual-AI")
st.caption("스마트 기술 문서 분석 및 코드 생성 봇")

# 사용자 질문 입력
if "messages" not in st.session_state:
    st.session_state.messages = []


# 이전 대화 내용 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("궁금한 기술이나 코드에 대해 질문해보세요!"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # RAG 체인 실행 및 답변 생성
        with st.spinner("답변을 생성하는 중입니다..."):
            retriever = load_retriever()
            prompt_template = get_rag_prompt()

            # Azure OpenAI LLM 모델 설정
            llm = AzureChatOpenAI(
                azure_endpoint=os.getenv("AOAI_ENDPOINT"),
                api_key=os.getenv("AOAI_API_KEY"),
                azure_deployment=os.getenv("AOAI_DEPLOY_GPT4O_MINI"), 
                api_version="2024-02-01",
                temperature=0.7 # 약간의 창의성을 부여
            )

            # RAG 체인 구성(설계도)
            rag_chain = (
                {"context": retriever, "question": RunnablePassthrough()}
                | prompt_template
                | llm
                | StrOutputParser()
            )

            # invoke가 실행되는 순간 위에서 선언해놨던 파이프라인이 실행되며 인스턴스가 된다.
            response = rag_chain.invoke(prompt)
            st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})