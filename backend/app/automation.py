from fastapi import APIRouter
from backend.app.services.automation import recommend, get_automation_logs
from pydantic import BaseModel
from backend.app.services.automation import run_automation, get_recommendations

router=APIRouter(prefix="/automation",tags=["automation"])

@router.post("/recommend")
def recommend_route():
    return recommend()

@router.get("/logs")
def get_logs_route():
    return get_automation_logs()

class AutomationRun(BaseModel):
    vm_name:str
    dry_run:bool=True

@router.post("/run")
def run_automation_route(payload:AutomationRun):
    return run_automation(payload.vm_name,payload.dry_run)

@router.get("/recommendations")
def get_recommendations_route(status: str | None = None):
    return get_recommendations(status)

