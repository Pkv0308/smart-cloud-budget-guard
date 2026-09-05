from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.app.services.budgets import create_budget,get_all_budgets, update_budget
from backend.app.services.cost_estimator import get_spend_summary

router=APIRouter(prefix="/budgets",tags=["budgets"])

class BudgetCreate(BaseModel):
    project:str
    monthly_limit:float
    warning_threshold_percent:float=75.0
    critical_threshold_percent:float=90.0

class BudgetUpdate(BaseModel):
    monthly_limit:float | None = None
    warning_threshold_percent: float | None = None
    critical_threshold_percent: float | None = None

@router.put("/{budget_id}")
def update_budget_route(budget_id:int, update:BudgetUpdate):
    result=update_budget(
        budget_id,
        update.monthly_limit,
        update.warning_threshold_percent,
        update.critical_threshold_percent,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Budget not found")
    return result

@router.post("/")
def create_budget_route(budget:BudgetCreate):
    return create_budget(
        budget.project,
        budget.monthly_limit,
        budget.warning_threshold_percent,
        budget.critical_threshold_percent
    )

@router.get("/")
def get_budgets_route():
    return get_all_budgets()

@router.get("/spend")
def get_spend_summary_route():
    return get_spend_summary()