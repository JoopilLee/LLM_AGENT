# meeting_room_agent/app/utils/building_manager.py - data/buildings/*.yml 로드

from pathlib import Path
from typing import Any, Dict

import yaml


DEFAULT_BUILDINGS_DIR = "data/buildings"


def _load_yml(base_dir: Path, filename: str) -> Any:
    path = base_dir / filename
    if not path.exists():
        raise FileNotFoundError(f"Buildings data not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_building_data(buildings_dir: str = None) -> tuple:
    """
    data/buildings/ 아래 building_ids.yml, floor_ids.yml을 로드합니다.

    Returns:
        (building_ids, floor_ids) - building_ids는 name->id, floor_ids는 building_id->층->[floor_id, rooms]
    """
    if buildings_dir is None:
        # app/utils 기준 → 프로젝트 루트(meeting_room_agent) = parent.parent.parent
        base = Path(__file__).resolve().parent.parent.parent / DEFAULT_BUILDINGS_DIR
    else:
        base = Path(buildings_dir)
    raw_building_ids = _load_yml(base, "building_ids.yml")
    raw_floor_ids = _load_yml(base, "floor_ids.yml")

    # building_ids: 키는 문자열(건물명), 값은 int 유지
    building_ids = {}
    for k, v in raw_building_ids.items():
        if k.startswith("#"):
            continue
        building_ids[str(k).strip()] = int(v)

    # floor_ids: 키는 int(building_id, 층번호), 값 구조 유지. YAML이 이미 int로 파싱한 경우 그대로 사용
    floor_ids = {}
    for bid_key, floors in raw_floor_ids.items():
        if isinstance(floors, dict) and floors:
            bid = int(bid_key) if not isinstance(bid_key, int) else bid_key
            floor_ids[bid] = {}
            for f_key, f_val in floors.items():
                fn = int(f_key) if not isinstance(f_key, int) else f_key
                floor_ids[bid][fn] = f_val

    return building_ids, floor_ids


def build_reservation_dict(building_ids: Dict, floor_ids: Dict) -> Dict:
    """building_ids, floor_ids로 예약 저장용 빈 reservation_dict 생성."""
    reservation_dict = {}
    for bid in building_ids.values():
        reservation_dict[bid] = {}
        if bid not in floor_ids:
            continue
        for floor_key, floor_val in floor_ids[bid].items():
            floor_id = floor_val[0]
            room_dict = floor_val[1]
            reservation_dict[bid][floor_id] = {}
            for room_id in room_dict.values():
                reservation_dict[bid][floor_id][room_id] = {}
    return reservation_dict
