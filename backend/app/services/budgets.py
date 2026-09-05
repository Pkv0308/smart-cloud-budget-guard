from backend.app.database import SessionLocal
from backend.app.database.models import Budget

def create_budget(project:str,monthly_limit:float, warning_threshold_percent:float=75.0,
                  critical_threshold_percent:float=90.0)->dict:
    db=SessionLocal()
    try:
        budget=Budget(
            project=project,
            monthly_limit=monthly_limit,
            warning_threshold_percent=warning_threshold_percent,
            critical_threshold_percent=critical_threshold_percent,
        )
        db.add(budget)
        db.commit()
        db.refresh(budget)
        return {
            "id":budget.id,
            "project":budget.project,
            "monthly_limit":float(budget.monthly_limit)
        }
    finally:
        db.close()

def update_budget(budget_id:int, monthly_limit:float=None,
                  warning_threshold_percent:float=None,
                  critical_threshold_percent:float=None)->dict | None:
    db=SessionLocal()
    try:
        budget=db.query(Budget).filter(Budget.id==budget_id).first()
        if not budget:
            return None
        if monthly_limit is not None:
            budget.monthly_limit=monthly_limit
        if warning_threshold_percent is not None:
            warning_threshold_percent=warning_threshold_percent
        if critical_threshold_percent is not None:
            critical_threshold_percent=critical_threshold_percent
        db.commit()
        db.refresh(budget)
        return{
            "id":budget.id,
            "project":budget.project,
            "monthly_limit":float(budget.monthly_limit)
        }
    finally:
        db.close()

def get_all_budgets()->list[dict]:
    db=SessionLocal()
    try:
        budgets=db.query(Budget).all()
        return[
            {
                "id":b.id,
                "project":b.project,
                "monthly_limit":b.monthly_limit,
                "warning_threshold_percent":float(b.warning_threshold_percent),
                "critical_threshold_percent":float(b.critical_threshold_percent),
            }
            for b in budgets
        ]
    finally:
        db.close()