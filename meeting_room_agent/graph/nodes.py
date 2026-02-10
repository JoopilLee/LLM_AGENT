# meeting_room_agent/graph/nodes.py - LangGraph 노드 정의

from datetime import datetime

from langchain_core.messages import HumanMessage, SystemMessage

from core.config import llm
from core.state import AgentState, BookSlots, CheckSlots, RouteOut
from tools.tools import TOOLS


def init_node(state: AgentState) -> AgentState:
    state.setdefault("intent", "Unknown")
    state.setdefault("params", {})
    state.setdefault("need_more", False)
    state.setdefault("ask_user", "")
    state.setdefault("plan", [])
    state.setdefault("tool_result", None)
    state.setdefault("final_answer", None)
    return state


def router_node(state: AgentState) -> AgentState:
    today = datetime.now().strftime("%Y-%m-%d")
    # 1단계: 의도만 분류
    route_system = """당신은 회의실 에이전트의 의도 분류기입니다. 사용자 쿼리의 의도(intent)만 판별하세요.
의도: Check(가용성 조회), Book(예약 생성), Change(예약 수정), Cancel(예약 취소), Mine(내 예약 목록), Unknown"""
    out = llm.with_structured_output(RouteOut, method="function_calling").invoke(
        [SystemMessage(content=route_system), HumanMessage(content=state["query"])]
    )
    state["intent"] = out.intent
    state["params"] = out.params or {}
    state["need_more"] = out.need_more
    state["ask_user"] = out.ask_user or ""

    # 2단계: Book/Check는 전용 스키마로 슬롯 추출 (한글 쿼리 → 영어 키 보장)
    if out.intent == "Book":
        extract_system = f"""한국어 회의실 예약 문장에서 아래 필드를 추출하세요. **오늘 날짜: {today}**
- building: 건물명 그대로 (에펠탑, 본관 등)
- floor: 층 수만 숫자 (17층 → 17)
- room: 회의실 호실 (1702-A 등)
- user_name: 예약자/주최자 이름
- purpose, title: 회의 목적/제목 (같으면 둘 다 같은 값)
- start, end: 반드시 YYYY-MM-DDTHH:MM. "오늘 15:00~16:00" → start="{today}T15:00", end="{today}T16:00\""""
        try:
            slots = llm.with_structured_output(BookSlots, method="function_calling").invoke(
                [SystemMessage(content=extract_system), HumanMessage(content=state["query"])]
            )
            state["params"] = {
                "building": slots.building,
                "floor": slots.floor,
                "room": slots.room,
                "user_name": slots.user_name,
                "purpose": slots.purpose,
                "title": slots.title,
                "start": slots.start,
                "end": slots.end,
            }
            required = [slots.building, slots.room, slots.user_name, slots.title, slots.start, slots.end]
            state["need_more"] = not all(required)
            if state["need_more"]:
                missing = []
                if not slots.building:
                    missing.append("건물")
                if not slots.room:
                    missing.append("방")
                if not slots.user_name:
                    missing.append("사용자 이름")
                if not slots.title:
                    missing.append("제목")
                if not slots.start or not slots.end:
                    missing.append("시작/종료 시간")
                state["ask_user"] = "다음 정보를 알려주세요: " + ", ".join(missing)
        except Exception:
            state["need_more"] = True
            state["ask_user"] = "예약에 필요한 정보를 파악하지 못했습니다. 건물, 층, 방, 시간, 예약자, 제목을 알려주세요."

    elif out.intent == "Check":
        extract_system = f"""한국어 회의실 가용성 조회 문장에서 아래 필드를 추출하세요. **오늘 날짜: {today}**
- building: 건물명, floor: 층 수 숫자, room: 회의실 호실
- start, end: YYYY-MM-DDTHH:MM. "오늘 10:00~11:00" → start="{today}T10:00", end="{today}T11:00\""""
        try:
            slots = llm.with_structured_output(CheckSlots, method="function_calling").invoke(
                [SystemMessage(content=extract_system), HumanMessage(content=state["query"])]
            )
            state["params"] = {
                "building": slots.building,
                "floor": slots.floor,
                "room": slots.room,
                "start": slots.start,
                "end": slots.end,
            }
            state["need_more"] = not all([slots.building, slots.room, slots.start, slots.end])
            if state["need_more"]:
                state["ask_user"] = "건물, 층, 방, 조회할 시간대(시작~종료)를 알려주세요."
        except Exception:
            state["need_more"] = True
            state["ask_user"] = "조회할 건물, 층, 방, 시간대를 알려주세요."

    return state


def reverse_questioner(state: AgentState) -> AgentState:
    q = state.get("ask_user") or "필요한 정보를 알려주세요."
    state["final_answer"] = q
    return state


def planner_node(state: AgentState) -> AgentState:
    intent_to_tool = {
        "Check": "CheckAvailability",
        "Book": "CreateBooking",
        "Change": "UpdateBooking",
        "Cancel": "CancelBooking",
        "Mine": "GetUserReservations",
    }
    tool = intent_to_tool.get(state["intent"])
    if not tool:
        state["final_answer"] = "요청을 이해하지 못했어요. (가능: 조회/예약/변경/취소/내예약)"
        return state
    state["plan"] = [tool]
    return state


def executor_node(state: AgentState) -> AgentState:
    if not state.get("plan"):
        return state
    tool_name = state["plan"][0]
    try:
        result = TOOLS[tool_name].invoke(state.get("params", {}))
        state["tool_result"] = result
    except Exception as e:
        state["tool_result"] = {"ok": False, "error": str(e)}
    return state


def reporter_node(state: AgentState) -> AgentState:
    sys = """당신은 회의실 비서입니다. 도구 결과(JSON)와 입력 파라미터를 바탕으로
사용자에게 한국어로 짧고 명확하게 답하세요. 핵심(방/시간/결과/대안)이 먼저 나오도록 작성하세요."""
    tool_json = state.get("tool_result") or {}
    params = state.get("params") or {}
    messages = [
        SystemMessage(content=sys),
        HumanMessage(content=f"params: {params}\nresult: {tool_json}"),
    ]
    text = llm.invoke(messages).content
    state["final_answer"] = text if isinstance(text, str) else ""
    return state
