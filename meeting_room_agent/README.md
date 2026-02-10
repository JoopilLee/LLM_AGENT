# meeting_room_agent

회의실 예약/조회를 위한 LangGraph 기반 에이전트입니다.  
빌딩·층·회의실 조회, 가용성 확인, 예약 생성·수정·취소, 내 예약 목록을 자연어로 처리합니다.

## 구조

- **app/** — 애플리케이션 코드 루트
  - **app/core/** — 설정(`config.py`), 상태(`state.py`)
  - **app/db/** — PostgreSQL 모델·세션·시드·리포지터리
  - **app/utils/** — 프롬프트 로더(`prompt_manager.py`), 빌딩 YAML 로더(`building_manager.py`)
  - **app/services/** — 빌딩 서비스(`building_service.py`), 예약 서비스(`reservation_service.py`)
  - **app/graph/** — 노드(`nodes.py`), 워크플로우(`workflow.py`)
  - **app/tools/** — 도구 스키마(`schemas.py`), 도구 정의(`tools.py`)
- **data/** — `buildings/`(건물·층 YAML), `prompts/`(프롬프트 `.yml`)
- **run.py** — CLI 진입점 | **server.py** — Docker용 API 서버

## 설정

프로젝트 루트(`meeting_room_agent/`)에 `.env`를 두고 다음 변수를 설정합니다.

| 변수 | 필수 | 설명 |
|------|------|------|
| `OPENAI_API_KEY` | O | OpenAI API 키 |
| `OPENAI_MODEL` | - | 기본값 `gpt-4.1` |
| `DB_HOST` | - | DB 호스트 (로컬: `localhost`, Docker 시 compose가 `db`로 덮어씀) |
| `DB_PORT` | - | 기본 `5432` |
| `DB_USER` | - | DB 사용자 |
| `DB_PASSWORD` | - | DB 비밀번호 |
| `DB_NAME` | - | DB 이름 (기본 `meeting_room`) |

예시는 `.env.example`을 참고하고, `cp .env.example .env` 후 값을 채우면 됩니다.

## 실행

### 로컬
```bash
pip install -r requirements.txt
python run.py
python run.py "에펠탑 17층 1702-A 오늘 15:00~16:00로 주간 회의 예약해줘. 주최자는 홍길동."
```

### Docker (DB 자동 생성·연결, API 서비스)
`.env`에 `OPENAI_API_KEY`와 `DB_*`(DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)를 설정한 뒤:

```bash
cd meeting_room_agent
docker-compose up --build
```

- **PostgreSQL**: `db` 컨테이너가 `.env`의 `DB_USER`/`DB_PASSWORD`/`DB_NAME`으로 DB 생성·기동
- **앱**: `env_file: .env`로 동일 DB 설정 사용, Docker 내부에서만 `DB_HOST=db`로 덮어써서 연결. 테이블 생성·시드 후 API 서버 `http://localhost:8000` 기동

**API 호출 예:**
```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"query": "에펠탑 17층 1702-A 오늘 15:00~16:00에 비었어?"}'
```

**헬스 체크:** `GET http://localhost:8000/health`

종료: `docker-compose down` (볼륨 유지). DB까지 삭제: `docker-compose down -v`

## 예시 쿼리

- `에펠탑 17층 1702-A 2025-08-13 10:00~11:00 비었어?` — 가용 여부
- `에펠탑 17층 1702-A 오늘 15:00~16:00 주간 회의 예약해줘. 주최자 홍길동` — 예약
- `예약 아이디 15473_1_1_20250813_1500 취소해줘` — 취소 (ID는 실제 예약 생성 시 안내됨)
- `홍길동 내 예약 보여줘` — 내 예약 목록
