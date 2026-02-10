# meeting_room_agent/app/db/seed.py - YAML 데이터로 빌딩/층/회의실 시드
# YAML의 floor_id/room_id는 건물별로 중복될 수 있으므로, DB에는 전역 유일 ID 부여
from sqlalchemy import func, select

from app.db.models import Building, Floor, Room
from app.db.session import get_session
from app.utils.building_manager import load_building_data


def seed_if_empty():
    """buildings가 비어 있으면 data/buildings YAML로 시드."""
    with get_session() as session:
        if session.scalar(select(func.count()).select_from(Building)) > 0:
            return
        building_ids, floor_ids = load_building_data()
        # Buildings (YAML id 유지)
        for name, bid in building_ids.items():
            session.add(Building(id=bid, name=name))
        session.flush()
        # Floors & Rooms: 전역 유일 ID 사용 (YAML id는 건물 간 중복 가능)
        floor_pk = 1
        room_pk = 1
        for building_id, floors in floor_ids.items():
            for floor_number, (_floor_id_yaml, room_dict) in floors.items():
                session.add(Floor(id=floor_pk, building_id=building_id, floor_number=floor_number))
                for room_name in room_dict.keys():
                    session.add(Room(id=room_pk, floor_id=floor_pk, name=room_name))
                    room_pk += 1
                floor_pk += 1
        session.flush()
