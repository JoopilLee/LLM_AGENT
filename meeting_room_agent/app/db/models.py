# meeting_room_agent/app/db/models.py - SQLAlchemy 모델
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Building(Base):
    __tablename__ = "buildings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)  # YAML 시드 ID 유지
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    floors: Mapped[list["Floor"]] = relationship("Floor", back_populates="building")


class Floor(Base):
    __tablename__ = "floors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)  # YAML 시드 ID 유지
    building_id: Mapped[int] = mapped_column(Integer, ForeignKey("buildings.id"), nullable=False)
    floor_number: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (UniqueConstraint("building_id", "floor_number", name="uq_floor_building_number"),)

    building: Mapped["Building"] = relationship("Building", back_populates="floors")
    rooms: Mapped[list["Room"]] = relationship("Room", back_populates="floor")


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)  # YAML 시드 ID 유지
    floor_id: Mapped[int] = mapped_column(Integer, ForeignKey("floors.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    __table_args__ = (UniqueConstraint("floor_id", "name", name="uq_room_floor_name"),)

    floor: Mapped["Floor"] = relationship("Floor", back_populates="rooms")
    reservations: Mapped[list["Reservation"]] = relationship("Reservation", back_populates="room")


class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reservation_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    building_id: Mapped[int] = mapped_column(Integer, ForeignKey("buildings.id"), nullable=False)
    floor_id: Mapped[int] = mapped_column(Integer, ForeignKey("floors.id"), nullable=False)
    room_id: Mapped[int] = mapped_column(Integer, ForeignKey("rooms.id"), nullable=False)
    user_name: Mapped[str] = mapped_column(String(100), nullable=False)
    purpose: Mapped[str] = mapped_column(String(200), default="")
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    start_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    room: Mapped["Room"] = relationship("Room", back_populates="reservations")
