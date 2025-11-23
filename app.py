import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from src.agent import app as devmanual_ai_app


def extract_text_from_message(message):
    """Gemini 및 LangChain 메시지 객체에서 텍스트를 안전하게 추출합니다."""
    # 1. .text 속성이 있는 경우 (일부 Google GenAI 모델 래퍼)
    if hasattr(message, 'text') and message.text:
        return message.text

    # 2. content가 문자열인 경우 (일반적인 경우)
    if isinstance(message.content, str):
        return message.content

    # 3. content가 리스트인 경우 (멀티모달 또는 복합 응답)
    if isinstance(message.content, list):
        text_parts = []
        for block in message.content:
            if isinstance(block, dict):
                if 'text' in block:
                    text_parts.append(block['text'])
                elif 'type' in block and block['type'] == 'text': # {'type': 'text', 'text': '...'} 형식
                     text_parts.append(block.get('text', ''))
            elif isinstance(block, str):
                text_parts.append(block)
        return ''.join(text_parts)

    # 4. 기타 경우 (문자열로 변환 시도)
    return str(message.content) if message.content else ""


# --- 페이지 설정 ---
st.set_page_config(
    page_title="DevManual-AI",
    page_icon="🤖",
    layout="wide"
)

st.title("👨‍💻 DevManual-AI")
st.caption("RAG와 LangGraph 기반의 기술 문서 분석 및 코드 생성 AI 에이전트")

# --- 세션 상태 초기화 ---
if "messages" not in st.session_state:    
    st.session_state.messages = [
        AIMessage(content="안녕하세요! DevManual-AI입니다. 기술 문서, 코드 생성, 웹 검색 등 무엇이든 물어보세요. 제가 가진 도구들을 사용해 최적의 답변을 찾아 드릴게요.")
    ]

# 이전 대화 내용 표시
for message in st.session_state.messages:
    if isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(extract_text_from_message(message))
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
        with st.spinner("AI가 생각 중입니다..."):
            try:
                # 슈퍼바이저 에이전트는 전체 대화 기록을 입력으로 받습니다.
                inputs = {"messages": st.session_state.messages}
                
                # 안정성을 위해 .invoke()를 사용해 최종 결과만 한번에 받습니다.
                response = devmanual_ai_app.invoke(inputs)
                
                # 슈퍼바이저의 최종 답변은 응답의 'messages' 리스트의 마지막에 있습니다.
                final_answer = response['messages'][-1]
                
                # 텍스트 추출
                final_text = extract_text_from_message(final_answer)

                # 최종 답변을 화면에 출력합니다.
                st.markdown(final_text)

                # 3. AI 메시지를 대화 기록에 추가
                # 상태 관리를 위해 단순화된 메시지 객체보다는 원본 객체나 텍스트를 저장하는 것이 좋을 수 있으나,
                # LangGraph와의 호환성을 위해 반환된 메시지 객체를 그대로 사용합니다.
                st.session_state.messages.append(final_answer)
            
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")