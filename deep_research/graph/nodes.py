# deep_research/graph/nodes.py - 검색 필요 판단, 쿼리 생성, 검색, 보고서 목표/작성, 달성 여부, 쿼리 정련
import time
from typing import Any, Dict

from langchain_core.prompts import ChatPromptTemplate

from core.config import llm, tavily_tool
from core.state import (
    GraphState,
    _dedup_results,
    _format_results_for_prompt,
    _limit_max,
    _trueish,
)


def assess_search_need_node(state: GraphState) -> Dict[str, Any]:
    question = state["question"]
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "당신은 사용자의 질문에 웹 검색이 필요한지 여부를 판정하는 엄격한 라우터입니다. "
         "오직 'True' 또는 'False'만 답변하세요. "
         "최신 사실, 가격, 법률, 최근 사건, 고유명사 검증, 외부 인용이 필요한 경우 True를 반환하세요. "
         "시간에 무관한 일반 지식이나 의견이라면 False를 반환하세요."),
        ("human", "질문: {question}\n웹 검색이 필요한가요? (True/False)")
    ])
    chain = prompt | llm
    resp = chain.invoke({"question": question}).content.strip()
    need_search = _trueish(resp)
    print(f"[판정] 검색 필요 여부 = {need_search}  (LLM 응답: {resp})")
    return {"need_search": need_search, "iterations": state.get("iterations", 0)}


def generate_queries_node(state: GraphState) -> Dict[str, Any]:
    question = state["question"]
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "사용자의 질문에 답하기 위한 웹 검색 쿼리를 구체적으로 생성하세요. "
         "중복 없이 1~3개 생성하고, 각 줄에 하나씩 작성하세요."),
        ("human", "현재 날짜 기준(Asia/Seoul).\n질문: {question}\n검색 쿼리:")
    ])
    chain = prompt | llm
    raw = chain.invoke({"question": question}).content
    queries = [q.strip("- •\t ").strip() for q in raw.split("\n") if q.strip()]
    queries = [q for q in queries if len(q) > 1][:3]
    if len(queries) < 2:
        queries = list(dict.fromkeys(queries + [question]))[:2]
    print(f"[쿼리 생성] {queries}")
    return {"queries": queries}


def search_node(state: GraphState) -> Dict[str, Any]:
    print("---검색 실행---")
    queries = state.get("queries") or [state["question"]]
    collected: list[Dict[str, str]] = []

    def _do_search(q: str, attempt: int = 0):
        try:
            res = tavily_tool.invoke({"query": q})
            for r in res.get("results", []):
                collected.append({
                    "title": r.get("title", "") or "",
                    "url": r.get("url", "") or "",
                    "content": r.get("content", "") or r.get("raw_content", "") or ""
                })
        except Exception as e:
            print(f"[검색 오류] {e}")
            if attempt == 0:
                time.sleep(1.2)
                _do_search(q, attempt=1)

    for q in queries:
        if len(collected) >= 10:
            break
        _do_search(q)

    collected = _dedup_results(collected)
    if len(collected) < 2:
        _do_search(state["question"])
        collected = _dedup_results(collected)
    collected = _limit_max(collected, max_n=10)
    print(f"[검색 결과] {len(collected)}개 수집 완료")
    return {"search_results": collected}


def generate_report_goal_node(state: GraphState) -> Dict[str, Any]:
    print("---보고서 목표 생성---")
    question = state["question"]
    search_results = state.get("search_results", [])
    prompt = ChatPromptTemplate.from_messages([
        ("system", "간결하고 검증 가능한 보고서 목표를 정의하세요. "
                   "범위, 핵심 질문, 전달물 형식, 성공 기준을 1~3문장으로 작성하세요."),
        ("human", "질문: {question}\n\n자료:\n{sources}\n\n목표만 작성하세요.")
    ])
    chain = prompt | llm
    goal = chain.invoke({
        "question": question,
        "sources": _format_results_for_prompt(search_results) if search_results else "(외부 자료 없음)"
    }).content.strip()
    print(f"[목표] {goal}")
    return {"report_goal": goal}


def synthesize_report_node(state: GraphState) -> Dict[str, Any]:
    print("---보고서 작성---")
    question = state["question"]
    results = state.get("search_results", [])
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "간결하고 증거 기반의 보고서를 작성하세요. "
         "구성: 개요, 발견사항, 분석, 한계, 결론. "
         "출처는 [n] 형식으로 인용하고, 불확실성은 명확히 언급하세요."),
        ("human", "질문: {question}\n\n자료:\n{sources}\n\n보고서를 작성하세요.")
    ])
    chain = prompt | llm
    report = chain.invoke({
        "question": question,
        "sources": _format_results_for_prompt(results) if results else "(외부 자료 없음)"
    }).content.strip()
    return {"report": report}


def check_goal_achieved_node(state: GraphState) -> Dict[str, Any]:
    print("---목표 달성 여부 판단---")
    report_goal = state.get("report_goal", "")
    report = state.get("report", "")
    sources = _format_results_for_prompt(state.get("search_results", []))
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "보고서가 목표를 달성했는지 판단하세요. "
         "엄격하게 'True' 또는 'False'만 반환하세요."),
        ("human",
         "보고서 목표:\n{goal}\n\n보고서:\n{report}\n\n출처:\n{sources}\n\n달성 여부:")
    ])
    chain = prompt | llm
    resp = chain.invoke({"goal": report_goal, "report": report, "sources": sources}).content.strip()
    achieved = _trueish(resp)
    print(f"[달성 여부] {achieved} (원본 응답: {resp})")
    return {"goal_achieved": achieved}


def refine_queries_node(state: GraphState) -> Dict[str, Any]:
    print("---쿼리 정련---")
    report_goal = state.get("report_goal", "")
    report = state.get("report", "")
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "목표와 현재 보고서를 바탕으로, 증거 부족을 해소할 수 있는 후속 검색 쿼리 최대 3개를 제안하세요."),
        ("human", "목표:\n{goal}\n\n현재 보고서:\n{report}\n\n쿼리:")
    ])
    chain = prompt | llm
    raw = chain.invoke({"goal": report_goal, "report": report}).content
    new_queries = [q.strip("- •\t ").strip() for q in raw.split("\n") if q.strip()]
    new_queries = [q for q in new_queries if len(q) > 1][:3]
    prev = state.get("queries", [])
    merged = list(dict.fromkeys(prev + new_queries))
    print(f"[정련된 쿼리] {new_queries}")
    return {"queries": merged, "iterations": state.get("iterations", 0) + 1}
