# ai_discussion/core/state.py - LangGraph 토론 상태 및 열거형 정의
from enum import Enum, auto
from typing import Dict, List, TypedDict


class SpeakerRole(Enum):
    """토론자 역할."""
    PRO = "pro_agent"
    CON = "con_agent"
    JUDGE = "judge"
    COMPLETED = "completed"


class DebateStatus(Enum):
    """토론 진행 상태."""
    ACTIVE = auto()
    JUDGED = auto()
    COMPLETED = auto()


class DebateState(TypedDict):
    """LangGraph 토론 상태 (RAG 필드 포함)."""
    topic: str
    messages: List[Dict]
    current_round: int
    max_rounds: int
    current_speaker: SpeakerRole
    debate_status: DebateStatus
    vector_store: object
    retrieved_docs: Dict[str, List]
    current_query: str
    current_context: str
