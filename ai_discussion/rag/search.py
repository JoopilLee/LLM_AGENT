# ai_discussion/rag/search.py - 검색어 개선 및 위키피디아 수집
import os
import streamlit as st
import wikipedia
import requests
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage

from core.config import llm

# SSL 검증 실패 시(프록시/방화벽): .env에 WIKIPEDIA_SSL_VERIFY=0 설정
_WIKI_SSL_VERIFY = os.getenv("WIKIPEDIA_SSL_VERIFY", "1").strip().lower() not in ("0", "false", "no")


def improve_search_query(topic: str, search_type: str = "general", language: str = "en"):
    """
    LLM을 사용하여 검색 질의어를 개선합니다.

    Args:
        topic: 원래 토론 주제
        search_type: "pro" (찬성), "con" (반대), "general" (일반) 중 하나
        language: 검색 언어 ("en" 또는 "ko")

    Returns:
        개선된 검색 질의어 목록 (최대 3개)
    """
    prompt_by_type = {
        "pro": f"'{topic}'에 대해 찬성하는 입장을 뒷받침할 수 있는 사실과 정보를 찾고자 합니다. 위키피디아 검색에 적합한 3개의 검색어를 제안해주세요. 각 검색어는 25자 이내로 작성하고 콤마로 구분하세요. 검색어만 제공하고 설명은 하지 마세요.",
        "con": f"'{topic}'에 대해 반대하는 입장을 뒷받침할 수 있는 사실과 정보를 찾고자 합니다. 위키피디아 검색에 적합한 3개의 검색어를 제안해주세요. 각 검색어는 25자 이내로 작성하고 콤마로 구분하세요. 검색어만 제공하고 설명은 하지 마세요.",
        "general": f"'{topic}'에 대한 객관적인 사실과 정보를 찾고자 합니다. 위키피디아 검색에 적합한 3개의 검색어를 제안해주세요. 각 검색어는 25자 이내로 작성하고 콤마로 구분하세요. 검색어만 제공하고 설명은 하지 마세요.",
    }

    messages = [
        SystemMessage(
            content="당신은 검색 전문가입니다. 주어진 주제에 대해 가장 관련성 높은 검색어를 제안해주세요."
        ),
        HumanMessage(content=prompt_by_type[search_type]),
    ]

    try:
        response = llm.invoke(messages)
        suggested_queries = [q.strip() for q in response.content.split(",")]
        return suggested_queries[:3]
    except Exception as e:
        st.warning(f"검색어 개선 중 오류 발생: {str(e)}")
        if search_type == "pro":
            return [f"{topic} advantages", f"{topic} benefits", f"{topic} support"]
        elif search_type == "con":
            return [f"{topic} disadvantages", f"{topic} problems", f"{topic} against"]
        return [topic]


def get_wikipedia_content(
    topic: str, language: str = "en", search_type: str = "general"
) -> list[Document]:
    """위키피디아에서 주제별 문서를 수집합니다. (Streamlit UI 피드백 포함)"""
    st.divider()
    orig_get = None
    if not _WIKI_SSL_VERIFY:
        orig_get = requests.get
        def _patched_get(*args, **kwargs):
            kwargs.setdefault("verify", False)
            return orig_get(*args, **kwargs)
        requests.get = _patched_get
    try:
        wikipedia.set_lang(language)
        improved_queries = improve_search_query(topic, search_type, language)
        st.info(f"개선된 검색어: {', '.join(improved_queries)}")

        documents = []

        for query in improved_queries:
            search_results = wikipedia.search(query, results=3)
            if not search_results:
                continue

            for page_title in search_results[:2]:
                try:
                    page = wikipedia.page(page_title, auto_suggest=False)
                    if any(
                        doc.metadata.get("topic") == page_title for doc in documents
                    ):
                        continue

                    if page.summary:
                        documents.append(
                            Document(
                                page_content=page.summary,
                                metadata={
                                    "source": f"wikipedia-{language}",
                                    "section": "summary",
                                    "topic": page_title,
                                    "query": query,
                                },
                            )
                        )

                    content = page.content
                    if content:
                        max_length = 5000
                        if len(content) > max_length:
                            content = content[:max_length]
                        documents.append(
                            Document(
                                page_content=content,
                                metadata={
                                    "source": f"wikipedia-{language}",
                                    "section": "content",
                                    "topic": page_title,
                                    "query": query,
                                },
                            )
                        )
                except (
                    wikipedia.exceptions.DisambiguationError,
                    wikipedia.exceptions.PageError,
                ):
                    continue

        if documents:
            st.success(f"{language} 언어로 {len(documents)}개의 문서를 찾았습니다.")
        return documents

    except Exception as e:
        st.error(f"위키피디아 검색 중 오류 발생: {str(e)}")
        return []
    finally:
        if orig_get is not None:
            requests.get = orig_get
