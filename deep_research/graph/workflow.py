# deep_research/graph/workflow.py - LangGraph 딥 리서치 워크플로우 정의
from langgraph.graph import END, StateGraph

from core.state import GraphState
from graph.nodes import (
    assess_search_need_node,
    check_goal_achieved_node,
    generate_queries_node,
    generate_report_goal_node,
    refine_queries_node,
    search_node,
    synthesize_report_node,
)
from graph.router import route_continue_or_stop, route_goal, route_need_search


def get_app():
    """딥 리서치 그래프를 컴파일해 앱 인스턴스를 반환합니다."""
    workflow = StateGraph(GraphState)

    workflow.add_node("assess_search_need", assess_search_need_node)
    workflow.add_node("generate_queries", generate_queries_node)
    workflow.add_node("search", search_node)
    workflow.add_node("generate_report_goal", generate_report_goal_node)
    workflow.add_node("synthesize_report", synthesize_report_node)
    workflow.add_node("check_goal_achieved", check_goal_achieved_node)
    workflow.add_node("refine_queries", refine_queries_node)

    workflow.set_entry_point("assess_search_need")

    workflow.add_conditional_edges(
        "assess_search_need",
        route_need_search,
        {"search": "generate_queries", "skip": "generate_report_goal"},
    )
    workflow.add_edge("generate_queries", "search")
    workflow.add_edge("search", "generate_report_goal")
    workflow.add_edge("generate_report_goal", "synthesize_report")
    workflow.add_edge("synthesize_report", "check_goal_achieved")

    workflow.add_conditional_edges(
        "check_goal_achieved",
        route_goal,
        {"done": END, "not_done": "refine_queries"},
    )
    workflow.add_conditional_edges(
        "refine_queries",
        route_continue_or_stop,
        {"continue": "search", "stop": "synthesize_report"},
    )

    return workflow.compile()
