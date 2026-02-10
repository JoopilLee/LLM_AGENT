# meeting_room_agent/app/core/state.py - LangGraph 에이전트 상태 및 라우터 출력 스키마
from typing import Any, Dict, List, Literal, Optional, TypedDict, Annotated

from pydantic import BaseModel, Field


class AgentState(TypedDict):
    query: Annotated[str, "사용자 입력 원문"]
    intent: Annotated[Literal["Check", "Book", "Change", "Cancel", "Mine", "Unknown"], "의도"]
    params: Annotated[Dict[str, Any], "슬롯/파라미터"]
    need_more: Annotated[bool, "필수 슬롯 부족 여부"]
    ask_user: Annotated[str, "부족 슬롯에 대해 사용자에게 물을 질문"]
    plan: Annotated[List[str], "실행할 도구 시퀀스(간단히 1개)"]
    tool_result: Annotated[Optional[Dict[str, Any]], "도구 실행 결과"]
    final_answer: Annotated[Optional[str], "최종 사용자 응답"]


class RouteOut(BaseModel):
    """라우터 노드 구조화 출력 (의도 + Change/Cancel/Mine용 params)."""
    intent: Literal["Check", "Book", "Change", "Cancel", "Mine", "Unknown"]
    params: Dict[str, Any] = Field(default_factory=dict)
    need_more: bool = False
    ask_user: str = ""


class BookSlots(BaseModel):
    """예약 생성용 슬롯 (한글 쿼리에서 추출)."""
    building: str = Field(description="건물명, 예: 에펠탑, 본관")
    floor: int = Field(description="층 수 숫자, 예: 17")
    room: str = Field(description="회의실 호실, 예: 1702-A")
    user_name: str = Field(description="예약자/주최자 이름")
    purpose: str = Field(description="회의 목적")
    title: str = Field(description="회의 제목")
    start: str = Field(description="시작 시각, 반드시 YYYY-MM-DDTHH:MM")
    end: str = Field(description="종료 시각, 반드시 YYYY-MM-DDTHH:MM")


class CheckSlots(BaseModel):
    """가용성 조회용 슬롯."""
    building: str = Field(description="건물명")
    floor: int = Field(description="층 수")
    room: str = Field(description="회의실 호실")
    start: str = Field(description="시작 시각 YYYY-MM-DDTHH:MM")
    end: str = Field(description="종료 시각 YYYY-MM-DDTHH:MM")
