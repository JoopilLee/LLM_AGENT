# meeting_room_agent/core/data.py - 빌딩/층/회의실 데이터 및 예약 CRUD

from datetime import datetime, date, timedelta
from typing import Union

# 빌딩 이름 -> ID (일반적인 예시)
building_ids = {
    "에펠탑": 15473,
    "본관": 57631,
    "별관107": 34561,
    "동관A": 21654,
    "동관B": 46213,
}

# 층 id ([층_id, {회의실_dict}])
floor_ids = {
    15473: {
        17: [21, {"1702-A": 45821, "1705": 67329, "1708-B": 29847, "1711-C": 83756, "1713": 51294, "1715-A": 94628}],
        18: [22, {"1801": 72583, "1803-B": 46719, "1807-A": 58942, "1809": 31675, "1812-C": 89234, "1813-B": 67451, "1815": 42896}],
        19: [23, {"1902-C": 75319, "1904": 48627, "1906-A": 83745, "1910-B": 59183, "1912": 71456, "1915-C": 36928}],
        20: [24, {"2001-A": 64829, "2003": 47352, "2005-B": 89174, "2008-C": 52637, "2011": 73895, "2013-A": 41758, "2015": 96284}],
        21: [25, {"2102": 58473, "2104-B": 71926, "2107-A": 43859, "2109": 86247, "2112-C": 59638, "2115": 74152}],
        22: [26, {"2203-C": 67485, "2205": 42971, "2207-A": 85396, "2210-B": 53748, "2212": 79164, "2213-C": 46829, "2215-A": 91537}],
        23: [27, {"2301": 74628, "2304-B": 58391, "2306-C": 47259, "2309-A": 83647, "2311": 69485, "2315": 52738}],
        24: [28, {"2402-A": 81749, "2405-C": 64382, "2407": 49571, "2410-B": 73846, "2412-A": 58293, "2413": 95167, "2415-B": 42758}],
        25: [29, {"2503": 67419, "2505-B": 84256, "2508-A": 51739, "2511-C": 76842, "2513": 43695, "2515-A": 89274}],
        26: [30, {"2601-C": 75394, "2604": 48627, "2607-B": 82159, "2609-A": 56483, "2612": 73846, "2615-C": 41957}],
        27: [31, {"2702": 69485, "2705-A": 84736, "2708-C": 52194, "2710": 76429, "2713-B": 43857, "2715": 91584, "2702-B": 58376}],
    },
    57631: {
        15: [16, {"1501-A": 83749, "1504": 56281, "1507-B": 74693, "1510-C": 42857, "1512": 69485, "1515-A": 93746}],
        16: [17, {"1603-B": 67294, "1605": 84751, "1608-A": 52639, "1611-C": 76184, "1613": 49572, "1615-B": 83956, "1602": 71438}],
        17: [18, {"1702-C": 58374, "1705-A": 84629, "1707": 47382, "1710-B": 73856, "1712": 59684, "1715": 86241}],
        18: [19, {"1801": 74593, "1803-A": 62847, "1806-C": 49571, "1809-B": 85739, "1811": 53746, "1813-A": 79264, "1815-C": 46829}],
        19: [20, {"1902-B": 67485, "1905": 84372, "1907-A": 51693, "1910-C": 78426, "1912-B": 43857, "1915": 96284}],
        20: [21, {"2003-A": 75819, "2006-C": 48627, "2008": 83745, "2011-B": 59472, "2013": 72846, "2015-A": 46382}],
        21: [22, {"2101": 68493, "2104-B": 85297, "2107-C": 52738, "2109": 74625, "2112-A": 47839, "2115-B": 91584, "2105": 63758}],
        22: [23, {"2202-C": 76384, "2205-A": 49571, "2208": 84629, "2210-B": 58374, "2213": 73856, "2215-C": 42697}],
        23: [24, {"2303": 67485, "2306-B": 84751, "2308-A": 52394, "2311-C": 79264, "2313": 46829, "2315": 93746}],
        24: [25, {"2401-A": 74628, "2404": 58392, "2407-C": 85739, "2409-B": 47283, "2412": 73856, "2415-A": 59684, "2403": 82157}],
        25: [26, {"2502-B": 68493, "2505": 84372, "2508-C": 51749, "2510-A": 76428, "2513": 43857, "2515-B": 92586}],
        26: [27, {"2603-C": 75384, "2606-A": 49571, "2608": 83749, "2611-B": 57293, "2613": 74625, "2615": 46829}],
    },
    34561: {
        14: [17, {"1402": 69485, "1405-A": 84736, "1408-C": 52194, "1411-B": 76429, "1413": 43857, "1415-A": 91584}],
        15: [18, {"1501-B": 67394, "1504": 85729, "1507-C": 48627, "1510-A": 73846, "1512": 59684, "1515": 84372, "1503": 52738}],
        16: [19, {"1602-A": 76485, "1605-C": 49571, "1608": 83749, "1611-B": 57294, "1613-A": 74628, "1615": 46829}],
        17: [20, {"1703": 68493, "1706-B": 85297, "1709-A": 52738, "1712-C": 79264, "1715": 43857, "1701": 94628, "1708": 67485}],
        18: [21, {"1802-C": 75394, "1805": 48627, "1808-A": 84729, "1811-B": 56283, "1813": 73856, "1815-C": 49571}],
        19: [22, {"1901": 67485, "1904-B": 85739, "1907-C": 52394, "1910-A": 78426, "1912": 43857, "1915": 96284, "1903": 74628}],
        20: [23, {"2002-A": 69485, "2005-C": 84736, "2008": 51794, "2011-B": 76429, "2013": 43857, "2015-A": 92586}],
        21: [24, {"2103-B": 75384, "2106": 48627, "2109-A": 83749, "2112-C": 57294, "2115": 74628, "2101": 46829}],
    },
    21654: {
        5: [10, {"502": 83749, "505-A": 67294, "508-B": 49571, "511": 85739, "513-C": 52738, "515": 76428, "507": 43857}],
        6: [11, {"601-C": 74693, "604": 58392, "607-A": 84729, "610-B": 46829, "612": 73856, "615-C": 59684}],
        7: [12, {"703": 68493, "706-B": 85297, "709-A": 52738, "712": 79264, "715-C": 43857, "701": 94628}],
        8: [13, {"802-A": 75394, "805-C": 48627, "808": 84729, "811-B": 56283, "813": 73856, "815": 49571, "804": 67485}],
        9: [14, {"901": 69485, "904-B": 85739, "907-C": 52394, "910": 78426, "912-A": 43857, "915": 96284}],
        10: [15, {"1002-C": 67485, "1005": 84736, "1008-A": 51794, "1011-B": 76429, "1013": 43857, "1015": 92586, "1007": 74628}],
        11: [16, {"1103": 75384, "1106-B": 48627, "1109-A": 83749, "1112": 57294, "1115-C": 74628, "1101": 46829}],
        12: [17, {"1202-A": 68493, "1205": 85297, "1208-C": 52738, "1211-B": 79264, "1213": 43857, "1215": 94628}],
        13: [18, {"1301-B": 75394, "1304-C": 48627, "1307": 84729, "1310-A": 56283, "1312": 73856, "1315": 49571, "1303": 67485}],
        14: [19, {"1402": 69485, "1405-A": 85739, "1408-C": 52394, "1411": 78426, "1413-B": 43857, "1415": 96284}],
        15: [20, {"1501": 67485, "1504-C": 84736, "1507-A": 51794, "1510": 76429, "1512-B": 43857, "1515": 92586, "1506": 74628}],
        16: [21, {"1603-B": 75384, "1606": 48627, "1609-A": 83749, "1612-C": 57294, "1615": 74628, "1601": 46829}],
        17: [22, {"1702": 68493, "1705-A": 85297, "1708": 52738, "1711-B": 79264, "1713-C": 43857, "1715": 94628, "1707": 75394}],
        18: [23, {"1801-C": 69485, "1804": 48627, "1807-B": 84729, "1810-A": 56283, "1812": 73856, "1815": 49571}],
    },
    46213: {
        7: [15, {"702-A": 83749, "705": 67294, "708-C": 49571, "711-B": 85739, "713": 52738, "715": 76428}],
        8: [16, {"801": 74693, "804-B": 58392, "807-A": 84729, "810": 46829, "812-C": 73856, "815": 59684, "803": 68493}],
        9: [17, {"903-C": 75394, "906": 48627, "909-B": 84729, "912-A": 56283, "915": 73856, "901": 49571}],
        10: [18, {"1002": 69485, "1005-A": 85739, "1008": 52394, "1011-C": 78426, "1013-B": 43857, "1015": 96284, "1007": 67485}],
        11: [19, {"1101-B": 75384, "1104": 48627, "1107-C": 83749, "1110": 57294, "1112-A": 74628, "1115": 46829}],
        12: [20, {"1203": 68493, "1206-A": 85297, "1209-B": 52738, "1212": 79264, "1215-C": 43857, "1201": 94628}],
        13: [21, {"1302-C": 75394, "1305": 48627, "1308-A": 84729, "1311-B": 56283, "1313": 73856, "1315": 49571, "1307": 67485}],
        14: [22, {"1401": 69485, "1404-B": 85739, "1407": 52394, "1410-C": 78426, "1412-A": 43857, "1415": 96284}],
        15: [23, {"1502-A": 67485, "1505": 84736, "1508-C": 51794, "1511": 76429, "1513-B": 43857, "1515": 92586}],
    },
}

# 예약 정보 저장 (building_id -> floor_id -> room_id -> reservation_id -> reservation)
reservation_dict: dict = {}
for bid in building_ids.values():
    reservation_dict[bid] = {}
    for floor_key, (floor_id, room_dict) in floor_ids[bid].items():
        reservation_dict[bid][floor_id] = {}
        for room_name, room_id in room_dict.items():
            reservation_dict[bid][floor_id][room_id] = {}

ISO_FMT = "%Y-%m-%dT%H:%M"


def parse_iso(s: str) -> datetime:
    return datetime.strptime(s, ISO_FMT)


def get_buildings():
    return building_ids


def get_floors(building_id):
    return {floor: floor_ids[building_id][floor][0] for floor in floor_ids[building_id]}


def get_rooms(building_id, floor_id):
    floors = get_floors(building_id)
    for floor_key in floors:
        if floors[floor_key] == floor_id:
            return floor_ids[building_id][floor_key][1]
    return None


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


def resolve_building_id(building: Union[str, int]) -> int:
    if isinstance(building, int):
        return building
    m = get_buildings()
    if building in m:
        return m[building]
    try:
        return int(building)
    except Exception:
        raise ValueError(f"알 수 없는 빌딩: {building}")


def resolve_floor_id(building_id: int, floor: Union[int, str]) -> int:
    floors = get_floors(building_id)
    if isinstance(floor, int) and floor in floors:
        return floors[floor]
    try:
        f = int(floor)
        if f in floors.values():
            return f
        if f in floors:
            return floors[f]
    except Exception:
        pass
    raise ValueError(f"알 수 없는 층: {floor} (building_id={building_id})")


def resolve_room_id(building_id: int, floor_id: int, room: Union[str, int]) -> int:
    rooms = get_rooms(building_id, floor_id)
    if rooms is None:
        raise ValueError(f"층 정보 없음 (building_id={building_id}, floor_id={floor_id})")
    if isinstance(room, int):
        if room in rooms.values():
            return room
        raise ValueError(f"알 수 없는 회의실 ID: {room}")
    if room in rooms:
        return rooms[room]
    try:
        r = int(room)
        if r in rooms.values():
            return r
    except Exception:
        pass
    raise ValueError(f"알 수 없는 회의실: {room} (building_id={building_id}, floor_id={floor_id})")


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
