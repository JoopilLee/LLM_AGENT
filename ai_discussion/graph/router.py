# ai_discussion/graph/router.py - 검색/에이전트 노드 간 라우팅
from typing import Literal

from core.state import DebateState, DebateStatus, SpeakerRole


def router(
    state: DebateState,
) -> Literal[
    "retrieve_pro_info",
    "pro_agent",
    "retrieve_con_info",
    "con_agent",
    "retrieve_judge_info",
    "judge",
    "END",
]:
    """현재 화자와 상태에 따라 다음 노드(검색 또는 END)를 반환합니다."""
    if state["debate_status"] == DebateStatus.COMPLETED:
        return "END"

    current_speaker = state["current_speaker"]

    if current_speaker == SpeakerRole.PRO:
        return "retrieve_pro_info"
    elif current_speaker == SpeakerRole.CON:
        return "retrieve_con_info"
    elif current_speaker == SpeakerRole.JUDGE:
        return "retrieve_judge_info"
    elif current_speaker == SpeakerRole.COMPLETED:
        return "END"


def pro_router(state: DebateState) -> Literal["pro_agent"]:
    return "pro_agent"


def con_router(state: DebateState) -> Literal["con_agent"]:
    return "con_agent"


def judge_router(state: DebateState) -> Literal["judge"]:
    return "judge"
