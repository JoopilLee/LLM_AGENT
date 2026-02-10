# meeting_room_agent/app/services/reservation_service.py - 예약 CRUD, 시간 겹침/빈 슬롯

from datetime import datetime, date

from app.services.store import reservation_dict

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
    room_reservations = reservation_dict[building_id][floor_id][room_id]
    for res_id, reservation in room_reservations.items():
        if exclude_reservation_id and res_id == exclude_reservation_id:
            continue
        existing_start = reservation["start_datetime"]
        existing_end = reservation["end_datetime"]
        if new_start < existing_end and new_end > existing_start:
            return True, res_id
    return False, None


def add_reservation(building_id, floor_id, room_id, user_name, purpose, title, start_datetime, end_datetime):
    reservation_id = generate_reservation_id(building_id, floor_id, room_id, start_datetime)
    is_overlap, conflicting_reservation_id = check_time_overlap(
        building_id, floor_id, room_id, start_datetime, end_datetime
    )
    if is_overlap:
        return False, f"예약이 겹칩니다. 충돌하는 예약: {conflicting_reservation_id}", None
    reservation_dict[building_id][floor_id][room_id][reservation_id] = {
        "building_id": building_id,
        "floor_id": floor_id,
        "room_id": room_id,
        "user_name": user_name,
        "purpose": purpose,
        "title": title,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
    }
    return True, "예약이 성공적으로 추가되었습니다.", reservation_id


def cancel_reservation(reservation_id):
    building_id, floor_id, room_id = parse_reservation_id(reservation_id)
    if building_id is None:
        return False, "잘못된 예약 ID 형식입니다."
    if (
        building_id in reservation_dict
        and floor_id in reservation_dict[building_id]
        and room_id in reservation_dict[building_id][floor_id]
        and reservation_id in reservation_dict[building_id][floor_id][room_id]
    ):
        del reservation_dict[building_id][floor_id][room_id][reservation_id]
        return True, "예약이 성공적으로 취소되었습니다."
    return False, "존재하지 않는 예약입니다."


def get_room_reservations(building_id, floor_id, room_id, date=None):
    if building_id not in reservation_dict or floor_id not in reservation_dict[building_id] or room_id not in reservation_dict[building_id][floor_id]:
        return []
    room_reservations = []
    for res_id, reservation in reservation_dict[building_id][floor_id][room_id].items():
        if date and reservation["start_datetime"].date() != date:
            continue
        room_reservations.append({"reservation_id": res_id, **reservation})
    room_reservations.sort(key=lambda x: x["start_datetime"])
    return room_reservations


def update_reservation(reservation_id, **kwargs):
    building_id, floor_id, room_id = parse_reservation_id(reservation_id)
    if building_id is None:
        return False, "잘못된 예약 ID 형식입니다."
    if (
        building_id not in reservation_dict
        or floor_id not in reservation_dict[building_id]
        or room_id not in reservation_dict[building_id][floor_id]
        or reservation_id not in reservation_dict[building_id][floor_id][room_id]
    ):
        return False, "존재하지 않는 예약입니다."
    old_reservation = reservation_dict[building_id][floor_id][room_id][reservation_id].copy()
    new_reservation = old_reservation.copy()
    new_reservation.update(kwargs)
    time_changed = "start_datetime" in kwargs or "end_datetime" in kwargs
    room_changed = "building_id" in kwargs or "floor_id" in kwargs or "room_id" in kwargs
    if time_changed or room_changed:
        new_reservation_id = generate_reservation_id(
            new_reservation["building_id"],
            new_reservation["floor_id"],
            new_reservation["room_id"],
            new_reservation["start_datetime"],
        )
        is_overlap, conflicting_reservation_id = check_time_overlap(
            new_reservation["building_id"],
            new_reservation["floor_id"],
            new_reservation["room_id"],
            new_reservation["start_datetime"],
            new_reservation["end_datetime"],
            exclude_reservation_id=reservation_id,
        )
        if is_overlap:
            return False, f"예약이 겹칩니다. 충돌하는 예약: {conflicting_reservation_id}"
        del reservation_dict[building_id][floor_id][room_id][reservation_id]
        final_reservation_id = new_reservation_id
        reservation_dict[new_reservation["building_id"]][new_reservation["floor_id"]][new_reservation["room_id"]][final_reservation_id] = new_reservation
        return True, f"예약이 성공적으로 수정되었습니다. 새 예약 ID: {final_reservation_id}"
    reservation_dict[building_id][floor_id][room_id][reservation_id] = new_reservation
    return True, "예약이 성공적으로 수정되었습니다."


def get_reservation(reservation_id):
    building_id, floor_id, room_id = parse_reservation_id(reservation_id)
    if building_id is None:
        return None
    if (
        building_id in reservation_dict
        and floor_id in reservation_dict[building_id]
        and room_id in reservation_dict[building_id][floor_id]
        and reservation_id in reservation_dict[building_id][floor_id][room_id]
    ):
        reservation = reservation_dict[building_id][floor_id][room_id][reservation_id]
        return {"reservation_id": reservation_id, **reservation}
    return None


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
