# meeting_room_agent

회의실 예약/조회를 위한 LangGraph 기반 에이전트입니다.  
빌딩·층·회의실 조회, 가용성 확인, 예약 생성·수정·취소, 내 예약 목록을 자연어로 처리합니다.

## 구조

- **app/** — 애플리케이션 코드 루트
  - **app/core/** — 설정(`config.py`), 상태(`state.py`)
  - **app/utils/** — 프롬프트 로더(`prompt_manager.py`), 빌딩 관리(`building_manager.py`)
  - **app/services/** — 데이터 저장소(`store.py`), 빌딩 서비스(`building_service.py`), 예약 서비스(`reservation_service.py`)
  - **app/graph/** — 노드(`nodes.py`), 워크플로우(`workflow.py`)
  - **app/tools/** — 도구 스키마(`schemas.py`), 도구 정의(`tools.py`)
- **data/** — `buildings/`(건물·층 YAML), `prompts/`(프롬프트 템플릿 `.yml`)
- **run.py** — CLI 진입점

## 설정

- **LLM_AGENT 루트**에 있는 `.env`를 사용합니다. 루트에 `OPENAI_API_KEY`를 설정하세요.
- (선택) `OPENAI_MODEL` 기본값은 `gpt-4.1`입니다.

## 실행

```bash
pip install -r requirements.txt
python run.py
python run.py "에펠탑 17층 1702-A 오늘 15:00~16:00로 주간 회의 예약해줘. 주최자는 홍길동."
```

## 예시 쿼리

- `에펠탑 17층 1702-A 2025-08-13 10:00~11:00 비었어?`
- `예약 아이디 15473_21_45821_20250813_1500 취소해줘`
