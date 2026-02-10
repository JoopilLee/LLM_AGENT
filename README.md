# LLM_AGENT

LLM·LangGraph 기반 에이전트 실습 및 예제 프로젝트

## 구성

| 폴더 | 설명 |
|------|------|
| **ai_discussion** | LangGraph + RAG 기반 AI 찬반 토론 (Streamlit). Wikipedia 검색 후 찬성/반대/심판이 토론합니다. |
| **deep_research** | LangGraph + Tavily 기반 딥 리서치. 질문에 따라 검색·보고서 목표·작성·달성 여부를 반복합니다. |
| **practice** | LangChain, LangGraph 기초 실습 |

## 공통 설정

- **시크릿**: 프로젝트 루트에 `.env` 생성

## 실행

```bash
# AI Discussion (Streamlit)
streamlit run ai_discussion/app.py

# 딥 리서치 (CLI)
python deep_research/run.py "질문 내용"
```

각 폴더의 `README.md`와 `requirements.txt`를 참고해 의존성을 설치 후 실행
