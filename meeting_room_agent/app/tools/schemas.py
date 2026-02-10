# meeting_room_agent/app/tools/schemas.py - 도구 입력 Pydantic 스키마

from typing import Optional, Union

from pydantic import BaseModel, Field, field_validator

from app.services import ISO_FMT, parse_iso


class BuildingRequired(BaseModel):
    building: Union[str, int] = Field(..., description="빌딩 키(에펠탑, 본관 등) 또는 ID")


class BuildingAndFloor(BaseModel):
    building: Union[str, int]
    floor: Union[int, str]


class CheckAvailabilityInput(BaseModel):
    building: Union[str, int]
    floor: Union[int, str]
    room: Union[str, int]
    start: str
    end: str

    @field_validator("end")
    @classmethod
    def _end_after_start(cls, v, info):
        s = info.data.get("start")
        if s:
            sd, ed = parse_iso(s), parse_iso(v)
            if ed <= sd:
                raise ValueError("종료시각은 시작시각 이후여야 합니다.")
        return v


class CreateBookingInput(BaseModel):
    building: Union[str, int]
    floor: Union[int, str]
    room: Union[str, int]
    user_name: str
    purpose: str
    title: str
    start: str
    end: str


class UpdateBookingInput(BaseModel):
    reservation_id: str
    building: Optional[Union[str, int]] = None
    floor: Optional[Union[int, str]] = None
    room: Optional[Union[str, int]] = None
    start: Optional[str] = None
    end: Optional[str] = None
    title: Optional[str] = None
    purpose: Optional[str] = None


class CancelBookingInput(BaseModel):
    reservation_id: str


class GetUserReservationsInput(BaseModel):
    user_name: str
    days_ahead: int = 7
    building: Optional[Union[str, int]] = None
