from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from celery.result import AsyncResult
from api.core.celery import celery_app
from celery_worker import run_crew_task

app = FastAPI()

class AgentRequest(BaseModel):
    query: str

class AgentResponse(BaseModel):
    task_id: str
    status: str

class ResultResponse(BaseModel):
    task_id: str
    status: str
    result: str

@app.post("/invoke", response_model=AgentResponse)
def invoke_agent(request: AgentRequest):
    """CrewAI 에이전트 실행을 비동기적으로 요청합니다."""
    task = run_crew_task.delay(request.query)
    return AgentResponse(task_id=task.id, status='PENDING')

@app.get("/results/{task_id}", response_model=ResultResponse)
def get_results(task_id: str):
    """Celery 작업 ID를 사용하여 에이전트 실행 결과를 조회합니다."""
    task_result = AsyncResult(task_id, app=celery_app)
    
    if task_result.ready():
        return ResultResponse(task_id=task_id, status=task_result.status, result=str(task_result.result))
    else:
        return ResultResponse(task_id=task_id, status=task_result.status, result="Agent is still working...")