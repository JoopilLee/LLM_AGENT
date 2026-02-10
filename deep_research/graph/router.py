# deep_research/graph/router.py - 검색/스킵, 목표 달성, 계속/중단 라우팅
from core.state import GraphState


def route_need_search(state: GraphState) -> str:
    return "search" if state.get("need_search") else "skip"


def route_goal(state: GraphState) -> str:
    return "done" if state.get("goal_achieved") else "not_done"


def route_continue_or_stop(state: GraphState) -> str:
    if state.get("iterations", 0) >= 3:
        return "stop"
    if len(state.get("search_results", [])) >= 10:
        return "stop"
    return "continue"
