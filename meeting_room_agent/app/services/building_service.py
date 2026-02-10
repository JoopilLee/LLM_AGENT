# meeting_room_agent/app/services/building_service.py - 빌딩/층/회의실 조회 및 ID 해석

from typing import Union

from app.services.store import building_ids, floor_ids


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
