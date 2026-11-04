from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.schemas import BudgetOut, SpendOut
from backend.app.services.budgets import create_budget, get_all_budgets, update_budget
from backend.app.services.cost_estimator import get_spend_summary

router = APIRouter(prefix="/budgets", tags=["budgets"])


class BudgetCreate(BaseModel):
    project: str = Field(min_length=1)
    monthly_limit: float = Field(gt=0)
    warning_threshold_percent: float = Field(default=75.0, ge=0, le=100)
    critical_threshold_percent: float = Field(default=90.0, ge=0, le=100)


class BudgetUpdate(BaseModel):
    monthly_limit: float | None = Field(default=None, gt=0)
    warning_threshold_percent: float | None = Field(default=None, ge=0, le=100)
    critical_threshold_percent: float | None = Field(default=None, ge=0, le=100)


@router.post("/", response_model=BudgetOut)
def create_budget_route(budget: BudgetCreate):
    return create_budget(
        budget.project,
        budget.monthly_limit,
        budget.warning_threshold_percent,
        budget.critical_threshold_percent,
    )


@router.get("/", response_model=list[BudgetOut])
def get_budgets_route():
    return get_all_budgets()


@router.get("/spend", response_model=list[SpendOut])
def get_spend_summary_route():
    return get_spend_summary()


@router.put("/{budget_id}", response_model=BudgetOut)
def update_budget_route(budget_id: int, update: BudgetUpdate):
    result = update_budget(
        budget_id,
        update.monthly_limit,
        update.warning_threshold_percent,
        update.critical_threshold_percent,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Budget not found")
    return result