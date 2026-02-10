# ai_discussion/core/config.py - 환경 변수 및 LLM/임베딩 설정
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# 프로젝트 루트(LLM_AGENT)의 .env 로드 (core/ 한 단계 더 들어가므로 parent x3)
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)


def get_llm() -> ChatOpenAI:
    """OpenAI Chat LLM 인스턴스 반환 (.env의 OPENAI_API_KEY 사용)."""
    return ChatOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        temperature=0.7,
    )


def get_embeddings() -> OpenAIEmbeddings:
    """OpenAI Embeddings 인스턴스 반환 (.env의 OPENAI_API_KEY 사용)."""
    return OpenAIEmbeddings(
        api_key=os.getenv("OPENAI_API_KEY"),
        model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
    )


# 앱 전역에서 사용할 단일 인스턴스
llm = get_llm()
embeddings = get_embeddings()


def check_env_set() -> tuple[bool, str]:
    """필수 환경 변수 설정 여부 확인. (모두 설정됨, 누락된 변수 목록 또는 빈 문자열)"""
    required = ["OPENAI_API_KEY"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        return False, ", ".join(missing)
    return True, ""


def get_connection_troubleshooting() -> str:
    """Connection error 발생 시 사용자에게 보여줄 안내 문구."""
    return """
    **연결 오류 해결 방법**
    - **.env**에 `OPENAI_API_KEY=sk-...` 가 올바르게 설정되어 있는지 확인
    - API 키가 유효한지(만료·revoke 여부) [OpenAI API Keys](https://platform.openai.com/api-keys)에서 확인
    - 회사/학교 네트워크·VPN·방화벽에서 api.openai.com 차단 여부 확인
    """
