# meeting_room_agent/app/db/repository.py - 빌딩/예약 DB 조회·저장
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, select

from app.db.models import Building, Floor, Reservation, Room
from app.db.session import get_session


def db_get_building_ids() -> Dict[str, int]:
    """건물명 -> id 딕셔너리."""
    with get_session() as session:
        rows = session.execute(select(Building.id, Building.name)).all()
        return {name: bid for bid, name in rows}


def db_get_floor_ids(building_id: int) -> Dict[int, int]:
    """층번호 -> floor_id 딕셔너리."""
    with get_session() as session:
        rows = session.execute(
            select(Floor.floor_number, Floor.id).where(Floor.building_id == building_id)
        ).all()
        return {fn: fid for fn, fid in rows}


def db_get_rooms(building_id: int, floor_id: int) -> Optional[Dict[str, int]]:
    """해당 층의 회의실명 -> room_id. 해당 floor가 해당 building 소속인지 확인."""
    with get_session() as session:
        floor = session.execute(
            select(Floor).where(and_(Floor.id == floor_id, Floor.building_id == building_id))
        ).unique().scalars().one_or_none()
        if not floor:
            return None
        rows = session.execute(select(Room.name, Room.id).where(Room.floor_id == floor_id)).all()
        return {name: rid for name, rid in rows}


def db_get_room_reservations(
    building_id: int, floor_id: int, room_id: int, day: Optional[date] = None
) -> List[Dict[str, Any]]:
    with get_session() as session:
        q = select(Reservation).where(
            and_(
                Reservation.building_id == building_id,
                Reservation.floor_id == floor_id,
                Reservation.room_id == room_id,
            )
        )
        rows = session.execute(q).unique().scalars().all()
        out = []
        for r in rows:
            if day and r.start_datetime.date() != day:
                continue
            out.append({
                "reservation_id": r.reservation_id,
                "building_id": r.building_id,
                "floor_id": r.floor_id,
                "room_id": r.room_id,
                "user_name": r.user_name,
                "purpose": r.purpose,
                "title": r.title,
                "start_datetime": r.start_datetime,
                "end_datetime": r.end_datetime,
            })
        out.sort(key=lambda x: x["start_datetime"])
        return out


def db_get_reservation(reservation_id: str) -> Optional[Dict[str, Any]]:
    with get_session() as session:
        r = session.execute(select(Reservation).where(Reservation.reservation_id == reservation_id)).unique().scalars().one_or_none()
        if not r:
            return None
        return {
            "reservation_id": r.reservation_id,
            "building_id": r.building_id,
            "floor_id": r.floor_id,
            "room_id": r.room_id,
            "user_name": r.user_name,
            "purpose": r.purpose,
            "title": r.title,
            "start_datetime": r.start_datetime,
            "end_datetime": r.end_datetime,
        }


def db_find_overlapping(
    building_id: int, floor_id: int, room_id: int,
    new_start: datetime, new_end: datetime,
    exclude_reservation_id: Optional[str] = None,
) -> Optional[str]:
    """겹치는 예약이 있으면 해당 reservation_id 반환, 없으면 None."""
    with get_session() as session:
        q = select(Reservation).where(
            and_(
                Reservation.building_id == building_id,
                Reservation.floor_id == floor_id,
                Reservation.room_id == room_id,
                Reservation.start_datetime < new_end,
                Reservation.end_datetime > new_start,
            )
        )
        if exclude_reservation_id:
            q = q.where(Reservation.reservation_id != exclude_reservation_id)
        row = session.execute(q).unique().scalars().first()
        return row.reservation_id if row else None


def db_add_reservation(
    reservation_id: str,
    building_id: int, floor_id: int, room_id: int,
    user_name: str, purpose: str, title: str,
    start_datetime: datetime, end_datetime: datetime,
) -> None:
    with get_session() as session:
        session.add(Reservation(
            reservation_id=reservation_id,
            building_id=building_id,
            floor_id=floor_id,
            room_id=room_id,
            user_name=user_name,
            purpose=purpose,
            title=title,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
        ))


def db_delete_reservation(reservation_id: str) -> bool:
    """삭제 성공 여부."""
    with get_session() as session:
        r = session.execute(select(Reservation).where(Reservation.reservation_id == reservation_id)).unique().scalars().one_or_none()
        if not r:
            return False
        session.delete(r)
        session.flush()
        return True


def db_update_reservation(reservation_id: str, **kwargs: Any) -> Optional[Reservation]:
    """업데이트할 레코드 반환 (세션 내). 호출 측에서 commit. 실제로는 get_session이 commit하므로 별도 세션에서 조회 후 수정."""
    with get_session() as session:
        r = session.execute(select(Reservation).where(Reservation.reservation_id == reservation_id)).unique().scalars().one_or_none()
        if not r:
            return None
        for k, v in kwargs.items():
            if hasattr(r, k):
                setattr(r, k, v)
        session.flush()
        return r


def db_get_user_reservations(
    user_name: str, start_day: date, end_day: date, building_id_filter: Optional[int] = None
) -> List[Dict[str, Any]]:
    from datetime import time
    start_begin = datetime.combine(start_day, time(0, 0))
    end_inclusive = datetime.combine(end_day, time(23, 59, 59))
    with get_session() as session:
        q = select(Reservation).where(
            and_(
                Reservation.user_name == user_name,
                Reservation.start_datetime <= end_inclusive,
                Reservation.end_datetime >= start_begin,
            )
        )
        if building_id_filter is not None:
            q = q.where(Reservation.building_id == building_id_filter)
        rows = session.execute(q).unique().scalars().all()
        items = [
            {
                "reservation_id": r.reservation_id,
                "building_id": r.building_id,
                "floor_id": r.floor_id,
                "room_id": r.room_id,
                "title": r.title,
                "purpose": r.purpose,
                "start": r.start_datetime,
                "end": r.end_datetime,
            }
            for r in rows
        ]
        items.sort(key=lambda x: (x["start"], x["reservation_id"]))
        return items
