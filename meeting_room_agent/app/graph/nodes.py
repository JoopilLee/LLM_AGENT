# meeting_room_agent/app/graph/nodes.py - LangGraph 노드 정의

from datetime import datetime

from langchain_core.messages import HumanMessage, SystemMessage

from app.core.config import llm
from app.core.state import AgentState, BookSlots, CheckSlots, RouteOut
from app.utils import PromptManager
from app.tools.tools import TOOLS

_prompt_manager = PromptManager()


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
    route_system = _prompt_manager.get("router_intent")
    out = llm.with_structured_output(RouteOut, method="function_calling").invoke(
        [SystemMessage(content=route_system), HumanMessage(content=state["query"])]
    )
    state["intent"] = out.intent
    state["params"] = out.params or {}
    state["need_more"] = out.need_more
    state["ask_user"] = out.ask_user or ""

    # 2단계: Book/Check는 전용 스키마로 슬롯 추출 (한글 쿼리 → 영어 키 보장)
    if out.intent == "Book":
        extract_system = _prompt_manager.get("book_slots_extract", today=today)
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
        extract_system = _prompt_manager.get("check_slots_extract", today=today)
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
    sys = _prompt_manager.get("reporter")
    tool_json = state.get("tool_result") or {}
    params = state.get("params") or {}
    messages = [
        SystemMessage(content=sys),
        HumanMessage(content=f"params: {params}\nresult: {tool_json}"),
    ]
    text = llm.invoke(messages).content
    state["final_answer"] = text if isinstance(text, str) else ""
    return state
