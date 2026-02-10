# meeting_room_agent/app/db/session.py - 엔진 및 세션
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_database_url
from app.db.models import Base

_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(
            get_database_url(),
            pool_pre_ping=True,
            echo=False,
        )
    return _engine


def get_session_factory():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """DB 세션 컨텍스트 매니저. with get_session() as session: ..."""
    factory = get_session_factory()
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db():
    """테이블 생성 및 필요 시 YAML 시드."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    from app.db.seed import seed_if_empty
    seed_if_empty()
