# meeting_room_agent/app/services/building_service.py - 빌딩/층/회의실 조회 및 ID 해석 (DB)

from typing import Union

from app.db.repository import db_get_building_ids, db_get_floor_ids, db_get_rooms


def get_buildings():
    return db_get_building_ids()


def get_floors(building_id):
    return db_get_floor_ids(building_id)


def get_rooms(building_id, floor_id):
    return db_get_rooms(building_id, floor_id)


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
