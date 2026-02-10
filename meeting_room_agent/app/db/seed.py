# meeting_room_agent/app/db/seed.py - YAML 데이터로 빌딩/층/회의실 시드
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
        # Buildings
        for name, bid in building_ids.items():
            session.add(Building(id=bid, name=name))
        session.flush()
        # Floors & Rooms
        for building_id, floors in floor_ids.items():
            for floor_number, (floor_id, room_dict) in floors.items():
                session.add(Floor(id=floor_id, building_id=building_id, floor_number=floor_number))
                for room_name, room_id in room_dict.items():
                    session.add(Room(id=room_id, floor_id=floor_id, name=room_name))
        session.flush()
