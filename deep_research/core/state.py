# deep_research/core/state.py - LangGraph 상태 및 유틸 함수
from typing import Any, Dict, List

from typing_extensions import TypedDict


class GraphState(TypedDict, total=False):
    question: str
    need_search: bool
    queries: List[str]
    search_results: List[Dict[str, str]]  # {title, url, content}
    report_goal: str
    report: str
    goal_achieved: bool
    iterations: int


def _dedup_results(items: List[Dict[str, str]]) -> List[Dict[str, str]]:
    seen = set()
    out = []
    for it in items:
        key = (it.get("url") or "").strip() or (it.get("title") or "").strip() or (it.get("content") or "")[:120]
        if key and key not in seen:
            seen.add(key)
            out.append(it)
    return out


def _limit_max(items: List[Dict[str, str]], max_n: int = 10) -> List[Dict[str, str]]:
    return items[:max_n] if len(items) > max_n else items


def _format_results_for_prompt(results: List[Dict[str, str]]) -> str:
    lines = []
    for i, r in enumerate(results, 1):
        lines.append(
            f"[{i}] {r.get('title','(제목 없음)')}\nURL: {r.get('url','')}\n{(r.get('content','') or '')[:1200]}\n"
        )
    return "\n".join(lines)


def _trueish(s: str) -> bool:
    s = (s or "").strip().lower()
    return s.startswith("t") or s in {"yes", "y", "1", "true", "참", "예", "네"}
