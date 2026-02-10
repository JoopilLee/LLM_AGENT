# 딥 리서치 (deep_research)

질문을 입력하면 **LangGraph + Tavily Search**로 웹 검색·보고서 목표 수립·작성·달성 여부 확인을 반복하는 딥 리서치 CLI 도구입니다.

- 검색 필요 여부 판단 → 필요 시 쿼리 생성·검색 (2~10개 결과)
- 보고서 목표 생성 → 보고서 작성 → 목표 달성 여부 확인
- 미달성 시 쿼리 정련 후 재검색 (최대 3회)

## 프로젝트 구조

```
deep_research/
├── __init__.py
├── run.py              # CLI 실행 (python deep_research/run.py "질문")
├── core/
│   ├── __init__.py
│   ├── config.py       # .env, LLM, Tavily 도구
│   └── state.py        # GraphState, 유틸 함수
├── graph/
│   ├── __init__.py
│   ├── nodes.py        # 검색 판단, 쿼리 생성, 검색, 목표/보고서/달성여부/정련
│   ├── router.py       # 라우팅 함수
│   └── workflow.py     # get_app()
└── README.md
```

## 의존성

```bash
pip install -r requirements.txt
```

## 환경 변수 (.env)

시크릿은 프로젝트 루트의 `.env`에 설정

- **OPENAI_API_KEY** (필수)
- **TAVILY_API_KEY** (필수)
- OPENAI_MODEL (선택, 기본 gpt-4o)

## 실행 방법

**프로젝트 루트(LLM_AGENT)에서:**

```bash
python deep_research/run.py "이번 시즌 삼성라이온즈 경기력 평가 보고서 작성해줘"
```

인자를 생략하면 기본 질문으로 실행됩니다.
