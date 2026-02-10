# meeting_room_agent - 회의실 예약 에이전트 (LangGraph + PostgreSQL)
FROM python:3.11-slim

WORKDIR /app

# 시스템 의존성 (psycopg2 빌드 시 필요 없음 - binary 사용)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY data/ ./data/
COPY run.py .
COPY server.py .

# API 서버 포트
EXPOSE 8000

# 기본: API 서버 실행 (진입 스크립트에서 DB 대기 후 시작)
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
