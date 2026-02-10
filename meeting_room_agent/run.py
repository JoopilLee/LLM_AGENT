# meeting_room_agent/run.py - 회의실 에이전트 실행 스크립트
"""
사용법 (meeting_room_agent 디렉터리에서):
  python run.py
  python run.py "에펠탑 17층 1702-A 오늘 15:00~16:00 비었어?"
"""
import sys
from pathlib import Path

# 스크립트 디렉터리(meeting_room_agent)를 path에 넣어 app 패키지 인식
sys.path.insert(0, str(Path(__file__).resolve().parent))

import app.core.config  # noqa: F401 - .env 로드
from app.core.config import check_env_set
from app.db.session import init_db
from app.graph.workflow import get_agent


def run(query: str) -> dict:
    """한 쿼리에 대해 회의실 에이전트를 실행하고 최종 상태를 반환합니다."""
    ok, missing = check_env_set()
    if not ok:
        raise RuntimeError(f"필수 환경 변수가 없습니다: {missing}. .env에 OPENAI_API_KEY를 설정하세요.")
    init_db()  # PostgreSQL 테이블 생성 및 YAML 시드
    agent = get_agent()
    return agent.invoke({"query": query})


if __name__ == "__main__":
    default_query = "에펠탑 17층 1702-A 2025-08-13 10:00~11:00 비었어?"
    user_query = sys.argv[1] if len(sys.argv) > 1 else default_query
    result = run(user_query)
    print(result.get("final_answer", ""))
