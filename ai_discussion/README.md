# AI 토론 (ai_discussion)

LangGraph + RAG를 활용한 AI 찬반 토론 Streamlit 앱입니다.

## 프로젝트 구조

```
ai_discussion/
├── __init__.py
├── app.py              # Streamlit 엔트리포인트
├── core/               # 앱 공통 (설정·상태)
│   ├── __init__.py
│   ├── config.py       # .env, LLM/임베딩, 연결 검사
│   └── state.py        # DebateState, SpeakerRole, DebateStatus
├── rag/                # RAG 파이프라인
│   ├── __init__.py
│   ├── search.py       # 검색어 개선, 위키피디아 수집
│   └── vectorstore.py  # FAISS 벡터 스토어 생성·검색
└── graph/              # LangGraph 워크플로우
    ├── __init__.py
    ├── nodes.py        # 검색 노드, 찬성/반대/심판 에이전트
    ├── router.py       # 노드 간 라우팅
    └── workflow.py     # 토론 그래프 정의
```

## 의존성

```bash
pip install -r requirements.txt
```

## 실행 방법

**프로젝트 루트(LLM_AGENT)에서:**

```bash
streamlit run ai_discussion/app.py
```

**환경 변수**: 시크릿은 루트 `.env` **`OPENAI_API_KEY`** 필수. (선택) `OPENAI_MODEL`, `OPENAI_EMBEDDING_MODEL`
