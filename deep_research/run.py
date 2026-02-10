# deep_research/run.py - 딥 리서치 실행 스크립트
"""
사용법 (LLM_AGENT 루트에서):
  python deep_research/run.py
  python deep_research/run.py "질문 내용"
"""
import sys

# 스크립트 디렉터리(deep_research)를 path에 넣어 core, graph 패키지 인식
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))

import core.config  # noqa: F401 - .env 로드
from graph.workflow import get_app


def run(question: str) -> dict:
    """한 질문에 대해 딥 리서치를 실행하고 최종 상태를 반환합니다."""
    app = get_app()
    return app.invoke({"question": question})


if __name__ == "__main__":
    question = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "이번 시즌 삼성라이온즈 경기력 평가 보고서 작성해줘"
    )
    result_state = run(question)

    print("\n\n===== 보고서 =====\n")
    print(result_state.get("report", ""))
    print("\n===== 목표 =====\n")
    print(result_state.get("report_goal", ""))
    print("\n===== 달성 여부 =====\n")
    print(result_state.get("goal_achieved", ""))
