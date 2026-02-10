# LLM_AGENT

LLM·LangGraph 기반 에이전트 실습 및 예제 프로젝트

## 구성

| 폴더 | 설명 |
|------|------|
| **meeting_room_agent** | LangGraph 기반 회의실 예약/조회 에이전트. 빌딩·층·회의실 조회, 가용성 확인, 예약 생성·수정·취소, 내 예약 목록을 자연어로 처리합니다. |
| **ai_discussion** | LangGraph + RAG 기반 AI 찬반 토론 (Streamlit). Wikipedia 검색 후 찬성/반대/심판이 토론합니다. |
| **deep_research** | LangGraph + Tavily 기반 딥 리서치. 질문에 따라 검색·보고서 목표·작성·달성 여부를 반복합니다. |
| **practice** | LangChain, LangGraph 기초 실습 |

## 실행 
- **시크릿**: 프로젝트 루트에 `.env` 생성
- 각 폴더의 `README.md`와 `requirements.txt`를 참고해 의존성을 설치 후 실행
