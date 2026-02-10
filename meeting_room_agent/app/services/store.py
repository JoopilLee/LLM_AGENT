# meeting_room_agent/app/services/store.py - 빌딩/예약 데이터 저장소 (로드된 상태 보유)

from app.utils.building_manager import build_reservation_dict, load_building_data

# data/buildings/*.yml에서 로드
building_ids, floor_ids = load_building_data()
reservation_dict = build_reservation_dict(building_ids, floor_ids)
