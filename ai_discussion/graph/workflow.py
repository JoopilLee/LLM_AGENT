# ai_discussion/graph/workflow.py - LangGraph 토론 워크플로우 정의
from langgraph.graph import END, StateGraph

from core.state import DebateState
from graph.nodes import (
    con_agent,
    judge_agent,
    pro_agent,
    retrieve_con_info,
    retrieve_judge_info,
    retrieve_pro_info,
)
from graph.router import router


def create_debate_graph() -> StateGraph:
    """찬성 → 반대 → (라운드 반복) → 심판 토론 그래프를 생성하고 컴파일합니다."""
    workflow = StateGraph(DebateState)

    workflow.add_node("retrieve_pro_info", retrieve_pro_info)
    workflow.add_node("retrieve_con_info", retrieve_con_info)
    workflow.add_node("retrieve_judge_info", retrieve_judge_info)
    workflow.add_node("pro_agent", pro_agent)
    workflow.add_node("con_agent", con_agent)
    workflow.add_node("judge", judge_agent)

    workflow.set_entry_point("retrieve_pro_info")

    workflow.add_edge("retrieve_pro_info", "pro_agent")
    workflow.add_edge("retrieve_con_info", "con_agent")
    workflow.add_edge("retrieve_judge_info", "judge")

    workflow.add_conditional_edges(
        "pro_agent",
        router,
        {
            "retrieve_pro_info": "retrieve_pro_info",
            "retrieve_con_info": "retrieve_con_info",
            "retrieve_judge_info": "retrieve_judge_info",
            "END": END,
        },
    )
    workflow.add_conditional_edges(
        "con_agent",
        router,
        {
            "retrieve_pro_info": "retrieve_pro_info",
            "retrieve_con_info": "retrieve_con_info",
            "retrieve_judge_info": "retrieve_judge_info",
            "END": END,
        },
    )
    workflow.add_conditional_edges(
        "judge",
        router,
        {
            "retrieve_pro_info": "retrieve_pro_info",
            "retrieve_con_info": "retrieve_con_info",
            "retrieve_judge_info": "retrieve_judge_info",
            "END": END,
        },
    )

    return workflow.compile()
