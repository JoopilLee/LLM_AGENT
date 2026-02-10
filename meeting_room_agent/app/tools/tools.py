# meeting_room_agent/app/tools/tools.py - 회의실 예약 도구 정의

from typing import Any, Dict, List, Optional, Union

from langchain_core.tools import tool

from app.services import (
    ISO_FMT,
    add_reservation,
    cancel_reservation,
    check_time_overlap,
    get_buildings,
    get_floors,
    get_reservation,
    get_rooms,
    get_user_reservations_list,
    parse_iso,
    resolve_building_id,
    resolve_floor_id,
    resolve_room_id,
    suggest_same_room_slots,
    update_reservation,
)
from app.tools.schemas import (
    BuildingAndFloor,
    BuildingRequired,
    CancelBookingInput,
    CheckAvailabilityInput,
    CreateBookingInput,
    GetUserReservationsInput,
    UpdateBookingInput,
)


@tool("ListBuildings")
def list_buildings() -> Dict[str, Any]:
    """빌딩 목록: {이름: id}"""
    return {"buildings": get_buildings()}


@tool("ListFloors", args_schema=BuildingRequired)
def list_floors(building: Union[str, int]) -> Dict[str, Any]:
    """해당 빌딩의 층 목록: {층수: floor_id}"""
    b_id = resolve_building_id(building)
    return {"building_id": b_id, "floors": get_floors(b_id)}


@tool("ListRooms", args_schema=BuildingAndFloor)
def list_rooms(building: Union[str, int], floor: Union[int, str]) -> Dict[str, Any]:
    """해당 빌딩/층의 회의실 목록: [{name, room_id}]"""
    b_id = resolve_building_id(building)
    f_id = resolve_floor_id(b_id, floor)
    rooms = get_rooms(b_id, f_id)
    return {
        "building_id": b_id,
        "floor_id": f_id,
        "rooms": [{"name": name, "room_id": rid} for name, rid in rooms.items()],
    }


@tool("CheckAvailability", args_schema=CheckAvailabilityInput)
def check_availability(
    building: Union[str, int], floor: Union[int, str], room: Union[str, int], start: str, end: str
) -> Dict[str, Any]:
    """요청 시간대의 방 예약 겹침 확인 + 간단 대안 제안"""
    b_id = resolve_building_id(building)
    f_id = resolve_floor_id(b_id, floor)
    r_id = resolve_room_id(b_id, f_id, room)
    s_dt, e_dt = parse_iso(start), parse_iso(end)
    overlap, conflict_res = check_time_overlap(b_id, f_id, r_id, s_dt, e_dt)
    if overlap:
        return {
            "ok": True,
            "available": False,
            "conflict_reservation_id": conflict_res,
            "suggestions": suggest_same_room_slots(b_id, f_id, r_id, s_dt, e_dt, n=3),
        }
    return {"ok": True, "available": True}


@tool("CreateBooking", args_schema=CreateBookingInput)
def create_booking(
    building: Union[str, int],
    floor: Union[int, str],
    room: Union[str, int],
    user_name: str,
    purpose: str,
    title: str,
    start: str,
    end: str,
) -> Dict[str, Any]:
    """회의실 예약 생성"""
    b_id = resolve_building_id(building)
    f_id = resolve_floor_id(b_id, floor)
    r_id = resolve_room_id(b_id, f_id, room)
    s_dt, e_dt = parse_iso(start), parse_iso(end)
    ok, msg, res_id = add_reservation(b_id, f_id, r_id, user_name, purpose, title, s_dt, e_dt)
    if not ok:
        return {"ok": False, "message": msg, "suggestions": suggest_same_room_slots(b_id, f_id, r_id, s_dt, e_dt, n=3)}
    return {"ok": True, "message": msg, "reservation_id": res_id}


@tool("UpdateBooking", args_schema=UpdateBookingInput)
def update_booking(
    reservation_id: str,
    building: Optional[Union[str, int]] = None,
    floor: Optional[Union[int, str]] = None,
    room: Optional[Union[str, int]] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    title: Optional[str] = None,
    purpose: Optional[str] = None,
) -> Dict[str, Any]:
    """예약 시간/방/제목/목적 수정"""
    updates: Dict[str, Any] = {}
    if building is not None:
        updates["building_id"] = resolve_building_id(building)
    if floor is not None:
        curr = get_reservation(reservation_id)
        if not curr and "building_id" not in updates:
            return {"ok": False, "error": "존재하지 않는 예약입니다."}
        b_for = updates.get("building_id", curr["building_id"] if curr else None)
        updates["floor_id"] = resolve_floor_id(b_for, floor)
    if room is not None:
        curr = get_reservation(reservation_id)
        if not curr and ("building_id" not in updates or "floor_id" not in updates):
            return {"ok": False, "error": "존재하지 않는 예약입니다."}
        b_for = updates.get("building_id", curr["building_id"])
        f_for = updates.get("floor_id", curr["floor_id"])
        updates["room_id"] = resolve_room_id(b_for, f_for, room)
    if start is not None:
        updates["start_datetime"] = parse_iso(start)
    if end is not None:
        updates["end_datetime"] = parse_iso(end)
    if title is not None:
        updates["title"] = title
    if purpose is not None:
        updates["purpose"] = purpose
    ok, msg = update_reservation(reservation_id, **updates)
    if not ok:
        curr = get_reservation(reservation_id)
        if not curr:
            return {"ok": False, "error": msg}
        b_id = updates.get("building_id", curr["building_id"])
        f_id = updates.get("floor_id", curr["floor_id"])
        r_id = updates.get("room_id", curr["room_id"])
        s_dt = updates.get("start_datetime", curr["start_datetime"])
        e_dt = updates.get("end_datetime", curr["end_datetime"])
        return {"ok": False, "message": msg, "suggestions": suggest_same_room_slots(b_id, f_id, r_id, s_dt, e_dt, n=3)}
    return {"ok": True, "message": msg}


@tool("CancelBooking", args_schema=CancelBookingInput)
def cancel_booking(reservation_id: str) -> Dict[str, Any]:
    """예약 취소"""
    ok, msg = cancel_reservation(reservation_id)
    return {"ok": ok, "message": msg}


@tool("GetUserReservations", args_schema=GetUserReservationsInput)
def get_user_reservations(
    user_name: str, days_ahead: int = 7, building: Optional[Union[str, int]] = None
) -> Dict[str, Any]:
    """내 예약 목록(오늘~N일) 조회. building으로 필터 가능"""
    from datetime import date, timedelta

    start_day = date.today()
    end_day = start_day + timedelta(days=days_ahead)
    b_filter = resolve_building_id(building) if building is not None else None
    raw = get_user_reservations_list(user_name, start_day, end_day, b_filter)
    items: List[Dict[str, Any]] = [
        {
            "reservation_id": r["reservation_id"],
            "building_id": r["building_id"],
            "floor_id": r["floor_id"],
            "room_id": r["room_id"],
            "title": r["title"],
            "purpose": r["purpose"],
            "start": r["start"].strftime(ISO_FMT) if hasattr(r["start"], "strftime") else r["start"],
            "end": r["end"].strftime(ISO_FMT) if hasattr(r["end"], "strftime") else r["end"],
        }
        for r in raw
    ]
    return {"ok": True, "count": len(items), "items": items}


TOOLS = {
    "ListBuildings": list_buildings,
    "ListFloors": list_floors,
    "ListRooms": list_rooms,
    "CheckAvailability": check_availability,
    "CreateBooking": create_booking,
    "UpdateBooking": update_booking,
    "CancelBooking": cancel_booking,
    "GetUserReservations": get_user_reservations,
}
