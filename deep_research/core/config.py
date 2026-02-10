# deep_research/core/config.py - 환경 변수, LLM, Tavily 검색 도구
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch

# 프로젝트 루트(LLM_AGENT)의 .env 로드
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)


def get_llm() -> ChatOpenAI:
    """OpenAI Chat LLM 인스턴스 (.env의 OPENAI_API_KEY, OPENAI_MODEL 사용)."""
    return ChatOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        temperature=0.2,
        max_retries=2,
    )


def get_tavily_tool() -> TavilySearch:
    """Tavily 검색 도구 (.env의 TAVILY_API_KEY 사용)."""
    return TavilySearch(
        max_results=5,
        topic="general",
        search_depth="advanced",
        include_raw_content=True,
        tavily_api_key=os.getenv("TAVILY_API_KEY"),
    )


llm = get_llm()
tavily_tool = get_tavily_tool()
