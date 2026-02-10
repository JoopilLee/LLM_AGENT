# ai_discussion/app.py - Streamlit 엔트리포인트 (LangGraph AI 토론)
import streamlit as st
from openai import APIConnectionError

import core.config  # noqa: F401 - load_dotenv 및 LLM/임베딩 초기화
from core.config import check_env_set, get_connection_troubleshooting
from core.state import DebateStatus, DebateState, SpeakerRole
from graph import create_debate_graph
from rag import create_vector_store

# 페이지 설정
st.set_page_config(page_title="AI 토론", page_icon="🤖", layout="wide")

st.title("🤖 AI 토론 - LangGraph & RAG 버전")
st.markdown(
    """
    ### 프로젝트 소개
    이 애플리케이션은 LangGraph를 활용하여 AI 에이전트 간의 토론 워크플로우를 구현합니다.
    찬성 측, 반대 측, 그리고 심판 역할의 AI가 주어진 주제에 대해 체계적으로 토론을 진행합니다.
    RAG(Retrieval-Augmented Generation)를 통해 외부 지식을 검색하여 더 강력한 논리를 펼칩니다.
    """
)

# 세션 스테이트 초기화
if "debate_active" not in st.session_state:
    st.session_state.debate_active = False
    st.session_state.debate_messages = []
    st.session_state.vector_store = None
    st.session_state.retrieved_docs = {"pro": [], "con": []}

# 사이드바: 설정
with st.sidebar:
    st.header("토론 설정")
    debate_topic = st.text_input(
        "토론 주제를 입력하세요:", "인공지능이 인간의 일자리를 대체해야 한다"
    )
    max_rounds = st.slider("토론 라운드 수", min_value=1, max_value=5, value=1)
    enable_rag = st.checkbox(
        "RAG 활성화", value=True, help="외부 지식을 검색하여 토론에 활용합니다."
    )
    show_sources = st.checkbox(
        "출처 표시", value=True, help="검색된 정보의 출처를 표시합니다."
    )

# 토론 시작
if not st.session_state.debate_active and st.button("토론 시작"):
    ok, missing = check_env_set()
    if not ok:
        st.error(f"환경 변수가 설정되지 않았습니다. 누락: **{missing}** — `.env` 파일을 확인해주세요.")
        st.stop()

    st.session_state.vector_store = None
    st.session_state.retrieved_docs = {"pro": [], "con": []}

    if enable_rag:
        with st.spinner("외부 지식을 수집하고 분석 중입니다..."):
            vector_store = create_vector_store(debate_topic)
            st.session_state.vector_store = vector_store
            if vector_store:
                st.success("외부 지식 검색 준비 완료!")
            else:
                st.warning(
                    "외부 지식 검색을 위한 준비에 실패했습니다. 기본 토론으로 진행합니다."
                )

    debate_graph = create_debate_graph()
    initial_state: DebateState = {
        "topic": debate_topic,
        "messages": [],
        "current_round": 1,
        "max_rounds": max_rounds,
        "current_speaker": SpeakerRole.PRO,
        "debate_status": DebateStatus.ACTIVE,
        "vector_store": st.session_state.vector_store,
        "retrieved_docs": {"pro": [], "con": []},
        "current_query": "",
        "current_context": "",
    }

    try:
        with st.spinner("토론이 진행 중입니다... 완료까지 잠시 기다려주세요."):
            result = debate_graph.invoke(initial_state)
            st.session_state.debate_messages = result["messages"]
            st.session_state.debate_active = True
            st.session_state.retrieved_docs = result.get(
                "retrieved_docs", {"pro": [], "con": []}
            )
        st.rerun()
    except APIConnectionError:
        st.error("**Azure OpenAI에 연결할 수 없습니다.** (Connection error)")
        st.markdown(get_connection_troubleshooting())
        st.stop()

# 토론 내용 표시
if st.session_state.debate_active:
    st.header(f"토론 주제: {debate_topic}")
    st.header("토론 진행 상황")

    messages = st.session_state.debate_messages
    total_rounds = len([m for m in messages if m["role"] == "찬성 측"])

    for round_num in range(1, total_rounds + 1):
        st.subheader(f"라운드 {round_num}")
        pro_index = (round_num - 1) * 2
        if pro_index < len(messages) and messages[pro_index]["role"] == "찬성 측":
            with st.container(border=True):
                st.markdown("**🔵 찬성 측:**")
                st.write(messages[pro_index]["content"])

        con_index = (round_num - 1) * 2 + 1
        if con_index < len(messages) and messages[con_index]["role"] == "반대 측":
            with st.container(border=True):
                st.markdown("**🔴 반대 측:**")
                st.write(messages[con_index]["content"])
        st.divider()

    if messages and messages[-1]["role"] == "심판":
        with st.container(border=True):
            st.subheader("🧑‍⚖️ 최종 평가")
            st.write(messages[-1]["content"])

    if (
        show_sources
        and st.session_state.retrieved_docs
        and (
            st.session_state.retrieved_docs.get("pro")
            or st.session_state.retrieved_docs.get("con")
        )
    ):
        with st.expander("사용된 참고 자료 보기"):
            st.subheader("찬성 측 참고 자료")
            for i, doc in enumerate(
                st.session_state.retrieved_docs.get("pro", [])[:3]
            ):
                st.markdown(f"**출처 {i+1}**")
                st.text(doc[:300] + "..." if len(doc) > 300 else doc)
                st.divider()
            st.subheader("반대 측 참고 자료")
            for i, doc in enumerate(
                st.session_state.retrieved_docs.get("con", [])[:3]
            ):
                st.markdown(f"**출처 {i+1}**")
                st.text(doc[:300] + "..." if len(doc) > 300 else doc)
                st.divider()

    if st.button("새 토론 시작"):
        st.session_state.debate_active = False
        st.session_state.debate_messages = []
        st.session_state.vector_store = None
        st.session_state.retrieved_docs = {"pro": [], "con": []}
        st.rerun()
