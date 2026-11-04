from fastapi import APIRouter
from backend.app.services.automation import recommend, get_automation_logs
from pydantic import BaseModel
from backend.app.services.automation import run_automation, get_recommendations
from backend.app.schemas import (
    AutomationLogOut, RecommendationOut, RecommendResult, RunResult,
)

router=APIRouter(prefix="/automation",tags=["automation"])

@router.post("/recommend", response_model=list[RecommendResult])
def recommend_route():
    return recommend()

@router.get("/logs", response_model=list[AutomationLogOut])
def get_logs_route():
    return get_automation_logs()

class AutomationRun(BaseModel):
    vm_name:str
    dry_run:bool=True

@router.post("/run", response_model=RunResult)
def run_automation_route(payload:AutomationRun):
    return run_automation(payload.vm_name,payload.dry_run)

@router.get("/recommendations", response_model=list[RecommendationOut])
def get_recommendations_route(status: str | None = None):
    return get_recommendations(status)

