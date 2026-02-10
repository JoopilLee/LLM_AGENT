# meeting_room_agent/core/config.py - 환경 변수 및 LLM 설정
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 프로젝트 루트(LLM_AGENT)의 .env 로드
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)


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


def check_env_set() -> tuple[bool, str]:
    """필수 환경 변수 설정 여부 확인."""
    required = ["OPENAI_API_KEY"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        return False, ", ".join(missing)
    return True, ""
