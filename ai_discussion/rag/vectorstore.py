# ai_discussion/rag/vectorstore.py - FAISS 벡터 스토어 생성 및 유사도 검색
import streamlit as st
from langchain_community.vectorstores import FAISS

from core.config import embeddings
from rag.search import get_wikipedia_content


@st.cache_resource
def create_vector_store(topic: str):
    """
    주제에 대해 영/한 위키 문서를 수집하고 FAISS 벡터 스토어를 생성합니다.
    """
    documents = []

    wiki_docs_en = get_wikipedia_content(topic, "en")
    if wiki_docs_en:
        documents.extend(wiki_docs_en)

    wiki_docs_ko = get_wikipedia_content(topic, "ko")
    if wiki_docs_ko:
        documents.extend(wiki_docs_ko)

    if not any(c.isascii() for c in topic):
        try:
            additional_docs = get_wikipedia_content(f"{topic} in English", "en")
            if additional_docs:
                documents.extend(additional_docs)
        except Exception:
            pass

    if documents:
        try:
            return FAISS.from_documents(documents, embeddings)
        except Exception as e:
            st.error(f"Vector DB 생성 중 오류 발생: {str(e)}")
            return None
    return None


def retrieve_relevant_info(query: str, vector_store, k: int = 3) -> tuple[str, list]:
    """
    벡터 스토어에서 쿼리와 유사한 문서를 검색해 컨텍스트 문자열과 문서 목록을 반환합니다.
    """
    if not vector_store:
        return "", []

    try:
        retrieved_docs = vector_store.similarity_search(query, k=k)
        context = ""
        for i, doc in enumerate(retrieved_docs):
            source = doc.metadata.get("source", "Unknown")
            section = doc.metadata.get("section", "")
            context += f"[문서 {i+1}] 출처: {source}"
            if section:
                context += f", 섹션: {section}"
            context += f"\n{doc.page_content}\n\n"
        return context, retrieved_docs
    except Exception:
        return "", []
