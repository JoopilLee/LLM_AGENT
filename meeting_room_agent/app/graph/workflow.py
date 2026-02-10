# meeting_room_agent/app/graph/workflow.py - 회의실 에이전트 LangGraph 워크플로우

from langgraph.graph import END, START, StateGraph

from app.core.state import AgentState
from app.graph.nodes import (
    executor_node,
    init_node,
    planner_node,
    reporter_node,
    reverse_questioner,
    router_node,
)


def _route_after_router(state: AgentState) -> str:
    return "ReverseQuestioner" if state.get("need_more") else "Planner"


def get_agent():
    """회의실 에이전트 그래프를 컴파일해 에이전트 인스턴스를 반환합니다."""
    graph = StateGraph(AgentState)
    graph.add_node("Init", init_node)
    graph.add_node("Router", router_node)
    graph.add_node("Planner", planner_node)
    graph.add_node("Executor", executor_node)
    graph.add_node("Reporter", reporter_node)
    graph.add_node("ReverseQuestioner", reverse_questioner)

    graph.add_edge(START, "Init")
    graph.add_edge("Init", "Router")
    graph.add_conditional_edges(
        "Router",
        _route_after_router,
        {"ReverseQuestioner": "ReverseQuestioner", "Planner": "Planner"},
    )
    graph.add_edge("ReverseQuestioner", END)
    graph.add_edge("Planner", "Executor")
    graph.add_edge("Executor", "Reporter")
    graph.add_edge("Reporter", END)

    return graph.compile()
