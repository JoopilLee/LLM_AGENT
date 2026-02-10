# meeting_room_agent/app/core/config.py - 환경 변수 및 LLM 설정
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# .env 로드: meeting_room_agent 루트 또는 LLM_AGENT 루트 (Docker에서는 /app/.env는 없고 env로 전달)
_root_app = Path(__file__).resolve().parent.parent.parent  # meeting_room_agent 또는 /app
_env_path = _root_app / ".env"
if _env_path.exists():
    load_dotenv(dotenv_path=_env_path)
else:
    load_dotenv(dotenv_path=_root_app.parent / ".env")  # LLM_AGENT 루트


def get_database_url() -> str:
    """PostgreSQL 연결 URL. .env에 DATABASE_URL 또는 DB_* 개별 변수 설정."""
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "")
    dbname = os.getenv("DB_NAME", "meeting_room")
    return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"


def get_llm() -> ChatOpenAI:
    """OpenAI Chat LLM 인스턴스 반환 (.env의 OPENAI_API_KEY 사용)."""
    return ChatOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        model=os.getenv("OPENAI_MODEL", "gpt-4.1"),
        temperature=0.2,
        max_retries=2,
        max_tokens=None,
    )


llm = get_llm()


def check_env_set() -> tuple:
    """필수 환경 변수 설정 여부 확인."""
    required = ["OPENAI_API_KEY"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        return False, ", ".join(missing)
    return True, ""


def check_db_configured() -> bool:
    """DB 연결 정보가 있는지 확인 (DATABASE_URL 또는 DB_*)."""
    if os.getenv("DATABASE_URL"):
        return True
    return bool(os.getenv("DB_HOST") or os.getenv("DB_USER") or os.getenv("DB_NAME"))
