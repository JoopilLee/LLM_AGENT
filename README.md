# LLM_AGENT

LLM·LangGraph 기반 에이전트 실습 및 예제 프로젝트입니다.

## 구성

| 폴더 | 설명 |
|------|------|
| **ai_discussion** | LangGraph + RAG 기반 AI 찬반 토론 (Streamlit). Wikipedia 검색 후 찬성/반대/심판이 토론합니다. |
| **deep_research** | LangGraph + Tavily 기반 딥 리서치. 질문에 따라 검색·보고서 목표·작성·달성 여부를 반복합니다. |
| **practice** | LangGraph 기초 실습 노트북 (ChatOpenAI + StateGraph). |

## 공통 설정

- **시크릿**: API 키 등은 코드에 넣지 않고 **`.env`**에만 작성합니다. (프로젝트 루트에 `.env` 생성)
- **.env 예시**: 각 하위 폴더의 README 또는 `.env.example` 참고. 루트 `.gitignore`에 `.env`가 포함되어 있어 Git에 올라가지 않습니다.

## 실행

```bash
# AI 토론 (Streamlit)
streamlit run ai_discussion/app.py

# 딥 리서치 (CLI)
python deep_research/run.py "질문 내용"
```

각 폴더의 `README.md`와 `requirements.txt`를 참고해 의존성을 설치한 뒤 실행하면 됩니다.
