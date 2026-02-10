# meeting_room_agent/server.py - Docker/로컬 API 서버 (회의실 에이전트 호출)
"""
사용법:
  uvicorn server:app --host 0.0.0.0 --port 8000
  curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d '{"query": "에펠탑 17층 비었어?"}'
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from run import run as agent_run

app = FastAPI(title="Meeting Room Agent", description="회의실 예약/조회 LangGraph 에이전트 API")


class RunRequest(BaseModel):
    query: str


class RunResponse(BaseModel):
    final_answer: str
    success: bool = True


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/run", response_model=RunResponse)
def run_agent(req: RunRequest):
    try:
        result = agent_run(req.query)
        answer = result.get("final_answer", "")
        return RunResponse(final_answer=answer, success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
