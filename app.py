import streamlit as st
from src.agent import app as devmanual_ai_app


# --- 페이지 설정 ---
st.set_page_config(
    page_title="DevManual-AI",
    page_icon="🤖"
)
st.title("👨‍💻 DevManual-AI")
st.caption("RAG와 LangGraph 기반의 기술 문서 분석 및 코드 생성 AI 에이전트")

# 사용자 질문 입력
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "안녕하세요! DevManual-AI입니다. 기술 문서에 대해 궁금한 점이나 코드 생성이 필요한 부분이 있다면 무엇이든 물어보세요."}
    ]

# 이전 대화 내용 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("궁금한 기술이나 코드에 대해 질문해보세요!"):
    # 1. 사용자 메시지를 대화 기록에 추가하고 화면에 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. AI 응답 생성 및 표시
    with st.chat_message("assistant"):
        with st.spinner("AI가 생각 중입니다..."):
            # LangGraph 호출
            inputs = {"question": prompt}
            response_generator = devmanual_ai_app.stream(inputs)

            # 스트리밍 응답을 실시간으로 표시
            full_response = ""
            message_placeholder = st.empty()
            for chunk in response_generator:
                if "answer" in chunk.get("rag_node", {}):
                    full_response += chunk["rag_node"]["answer"]
                    message_placeholder.markdown(full_response + "▌")
                elif "answer" in chunk.get("code_generation_node", {}):
                    full_response += chunk["code_generation_node"]["answer"]
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})