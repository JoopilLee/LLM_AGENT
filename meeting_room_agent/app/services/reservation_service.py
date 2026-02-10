# meeting_room_agent/app/services/reservation_service.py - 예약 CRUD, 시간 겹침/빈 슬롯 (DB)

from datetime import datetime, date

from app.db.repository import (
    db_add_reservation,
    db_delete_reservation,
    db_find_overlapping,
    db_get_reservation,
    db_get_room_reservations,
    db_get_user_reservations,
    db_update_reservation,
)

ISO_FMT = "%Y-%m-%dT%H:%M"


def parse_iso(s: str) -> datetime:
    return datetime.strptime(s, ISO_FMT)


def generate_reservation_id(building_id, floor_id, room_id, start_datetime):
    timestamp = start_datetime.strftime("%Y%m%d_%H%M")
    return f"{building_id}_{floor_id}_{room_id}_{timestamp}"


def parse_reservation_id(reservation_id):
    parts = reservation_id.split("_")
    if len(parts) >= 4:
        return int(parts[0]), int(parts[1]), int(parts[2])
    return None, None, None


def check_time_overlap(building_id, floor_id, room_id, new_start, new_end, exclude_reservation_id=None):
    conflict = db_find_overlapping(
        building_id, floor_id, room_id, new_start, new_end, exclude_reservation_id
    )
    return (True, conflict) if conflict else (False, None)


def add_reservation(building_id, floor_id, room_id, user_name, purpose, title, start_datetime, end_datetime):
    reservation_id = generate_reservation_id(building_id, floor_id, room_id, start_datetime)
    is_overlap, conflicting_reservation_id = check_time_overlap(
        building_id, floor_id, room_id, start_datetime, end_datetime
    )
    if is_overlap:
        return False, f"예약이 겹칩니다. 충돌하는 예약: {conflicting_reservation_id}", None
    db_add_reservation(
        reservation_id, building_id, floor_id, room_id,
        user_name, purpose, title, start_datetime, end_datetime,
    )
    return True, "예약이 성공적으로 추가되었습니다.", reservation_id


def cancel_reservation(reservation_id):
    building_id, floor_id, room_id = parse_reservation_id(reservation_id)
    if building_id is None:
        return False, "잘못된 예약 ID 형식입니다."
    ok = db_delete_reservation(reservation_id)
    return (True, "예약이 성공적으로 취소되었습니다.") if ok else (False, "존재하지 않는 예약입니다.")


def get_room_reservations(building_id, floor_id, room_id, date=None):
    raw = db_get_room_reservations(building_id, floor_id, room_id, day=date)
    return [{"reservation_id": r["reservation_id"], **r} for r in raw]


def update_reservation(reservation_id, **kwargs):
    building_id, floor_id, room_id = parse_reservation_id(reservation_id)
    if building_id is None:
        return False, "잘못된 예약 ID 형식입니다."
    existing = db_get_reservation(reservation_id)
    if not existing:
        return False, "존재하지 않는 예약입니다."
    new_reservation = {**existing, **kwargs}
    time_changed = "start_datetime" in kwargs or "end_datetime" in kwargs
    room_changed = "building_id" in kwargs or "floor_id" in kwargs or "room_id" in kwargs
    if time_changed or room_changed:
        new_reservation_id = generate_reservation_id(
            new_reservation["building_id"],
            new_reservation["floor_id"],
            new_reservation["room_id"],
            new_reservation["start_datetime"],
        )
        is_overlap, conflicting = check_time_overlap(
            new_reservation["building_id"],
            new_reservation["floor_id"],
            new_reservation["room_id"],
            new_reservation["start_datetime"],
            new_reservation["end_datetime"],
            exclude_reservation_id=reservation_id,
        )
        if is_overlap:
            return False, f"예약이 겹칩니다. 충돌하는 예약: {conflicting}"
        db_delete_reservation(reservation_id)
        db_add_reservation(
            new_reservation_id,
            new_reservation["building_id"],
            new_reservation["floor_id"],
            new_reservation["room_id"],
            new_reservation["user_name"],
            new_reservation["purpose"],
            new_reservation["title"],
            new_reservation["start_datetime"],
            new_reservation["end_datetime"],
        )
        return True, f"예약이 성공적으로 수정되었습니다. 새 예약 ID: {new_reservation_id}"
    db_update_reservation(
        reservation_id,
        user_name=new_reservation.get("user_name"),
        purpose=new_reservation.get("purpose"),
        title=new_reservation.get("title"),
        start_datetime=new_reservation.get("start_datetime"),
        end_datetime=new_reservation.get("end_datetime"),
    )
    return True, "예약이 성공적으로 수정되었습니다."


def get_reservation(reservation_id):
    return db_get_reservation(reservation_id)


def find_gaps_for_day(building_id: int, floor_id: int, room_id: int, day: date):
    res_list = get_room_reservations(building_id, floor_id, room_id, date=day)
    open_t = datetime.combine(day, datetime.min.time()).replace(hour=9, minute=0)
    close_t = datetime.combine(day, datetime.min.time()).replace(hour=19, minute=0)
    gaps, cursor = [], open_t
    for r in res_list:
        s, e = r["start_datetime"], r["end_datetime"]
        if cursor < s:
            gaps.append((cursor, s))
        cursor = max(cursor, e)
    if cursor < close_t:
        gaps.append((cursor, close_t))
    return gaps


def suggest_same_room_slots(b_id: int, f_id: int, r_id: int, req_start: datetime, req_end: datetime, n=3):
    dur = req_end - req_start
    out = []
    for gs, ge in find_gaps_for_day(b_id, f_id, r_id, req_start.date()):
        if gs + dur <= ge:
            out.append({"start": (gs).strftime(ISO_FMT), "end": (gs + dur).strftime(ISO_FMT)})
        if len(out) >= n:
            break
    return out


def get_user_reservations_list(user_name: str, start_day: date, end_day: date, building_id_filter=None):
    """내 예약 목록 (도구용). 반환: [{"reservation_id", "building_id", "floor_id", "room_id", "title", "purpose", "start", "end"}, ...]"""
    return db_get_user_reservations(user_name, start_day, end_day, building_id_filter)
