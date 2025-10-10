import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from src.agent import app as devmanual_ai_app


# --- 페이지 설정 ---
st.set_page_config(
    page_title="DevManual-AI",
    page_icon="🤖"
)
st.title("👨‍💻 DevManual-AI")
st.caption("기술 문서 분석 및 코드 생성 AI 에이전트")

# --- 세션 상태 초기화 ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        AIMessage(content="안녕하세요! DevManual-AI입니다. 기술 문서, 코드 생성, 웹 검색 등 무엇이든 물어보세요. 제가 가진 도구들을 사용해 최적의 답변을 찾아 드릴게요.")
    ]

# 이전 대화 내용 표시
for message in st.session_state.messages:
    # langchain의 AIMessage, HumanMessage 객체의 role 속성을 확인합니다.
    if isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)

if prompt := st.chat_input("궁금한 기술이나 코드에 대해 질문해보세요!"):
    # 1. 사용자 메시지를 대화 기록에 추가하고 화면에 표시
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. AI 응답 생성 및 표시
    with st.chat_message("assistant"):
        with st.spinner("AI가 여러 도구를 사용해 생각 중입니다..."):
            inputs = {"messages": st.session_state.messages}
            
            # 스트리밍을 위한 빈 공간(placeholder) 생성
            message_placeholder = st.empty()
            full_response_content = ""

            # .stream()을 사용해서 실시간으로 청크를 받음
            for chunk in devmanual_ai_app.stream(inputs):
                # 스트림 청크에서 슈퍼바이저의 최종 답변 부분만 필터링
                if "messages" in chunk:
                    # 마지막 메시지의 content 조각을 계속 이어붙임
                    last_message = chunk["messages"][-1]
                    if isinstance(last_message, AIMessage) and last_message.content:
                         full_response_content += last_message.content
                         message_placeholder.markdown(full_response_content + "▌")
            
            # 최종적으로 커서 없이 완성된 답변을 표시
            message_placeholder.markdown(full_response_content)
            
    s# 전체 대화 기록에 최종 AI 답변을 추가
    if full_response_content:
        st.session_state.messages.append(AIMessage(content=full_response_content))