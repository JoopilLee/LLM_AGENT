#!/bin/sh
set -e

# PostgreSQL 연결 대기 (docker-compose에서 postgres가 준비될 때까지)
if [ -n "$DATABASE_URL" ] || [ -n "$DB_HOST" ]; then
  echo "Waiting for PostgreSQL..."
  host="${DB_HOST:-localhost}"
  port="${DB_PORT:-5432}"
  for i in $(seq 1 30); do
    if python -c "
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(2)
try:
  s.connect(('$host', $port))
  s.close()
  exit(0)
except Exception:
  exit(1)
" 2>/dev/null; then
    echo "PostgreSQL is ready."
    break
  fi
  if [ $i -eq 30 ]; then
    echo "Timeout waiting for PostgreSQL."
    exit 1
  fi
  sleep 1
  done
fi

# DB 테이블 생성 및 시드 (run.py의 init_db 호출)
echo "Initializing database..."
python -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('.').resolve()))
from app.db.session import init_db
init_db()
print('Database initialized.')
"

# API 서버 실행
exec uvicorn server:app --host 0.0.0.0 --port 8000
