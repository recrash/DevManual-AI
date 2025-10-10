import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END
from langchain_openai import AzureChatOpenAI

from .tools import rag_tool, code_gen_tool, search_tool

# --- 1. 에이전트 상태(State) 정의 ---
# 대화 기록(messages)을 중심으로 상태를 관리합니다.
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

# --- 2. 슈퍼바이저(Supervisor) 생성 ---
# 사용할 도구들을 리스트로 묶습니다.
tools = [rag_tool, code_gen_tool, search_tool]

# 도구들을 LLM이 이해할 수 있는 형태로 변환합니다.
llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AOAI_ENDPOINT"),
    api_key=os.getenv("AOAI_API_KEY"),
    azure_deployment=os.getenv("AOAI_DEPLOY_GPT4O_MINI"),
    api_version="2024-02-01",
    temperature=0
).bind_tools(tools)

# 슈퍼바이저 역할을 할 LLM 체인을 정의합니다.
# 이 체인은 대화 기록을 보고, 다음 행동(어떤 도구를 호출할지, 아니면 끝낼지)을 결정합니다.
supervisor_chain = (
    llm
)

# --- 3. 그래프(Graph) 구성 ---
# 에이전트 노드: 슈퍼바이저가 다음 행동을 결정하는 노드
def agent_node(state):
    print("---supervisor node 실행---")
    response = supervisor_chain.invoke(state["messages"]) 
    return {"messages": [response]}

# 도구 노드: 슈퍼바이저의 결정을 받아 실제 도구를 실행하는 노드
from langgraph.prebuilt import ToolNode
tool_node = ToolNode(tools)

# 조건부 엣지: 도구 실행 후, 계속할지 끝낼지 결정하는 로직
def should_continue(state):
    print("---다음 노드 결정---")
    # 마지막 메시지가 tool_calls를 가지고 있다면, 아직 할 일이 남았다는 의미입니다.
    if state["messages"][-1].tool_calls:
        print("경로: 도구 실행")
        return "tool_node"
    else:
        print("경로: 종료")
        return END
    
#그래프 정의
workflow = StateGraph(AgentState)

#노드 추가
workflow.add_node("agent_node", agent_node)
workflow.add_node("tool_node", tool_node)

#워크플로우 시작점
workflow.set_entry_point("agent_node")

#조건부 엣지 추가
workflow.add_conditional_edges(
    "agent_node",
    should_continue,
    {
        "tool_node": "tool_node",
        END: END,
    },
)

# 도구 노드 실행 후에는 항상 다시 'agent_node'(슈퍼바이저)로 돌아가서 검토를 받습니다. (루프 구조)
workflow.add_edge("tool_node", "agent_node")


# --- 4. 그래프 컴파일 및 실행 ---
load_dotenv(dotenv_path="../.env")

app = workflow.compile()