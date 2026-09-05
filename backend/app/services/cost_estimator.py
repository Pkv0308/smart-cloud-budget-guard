from datetime import datetime
from backend.app.database import SessionLocal
from backend.app.database.models import Resource
from backend.app.budgets import get_all_budgets
# Mock hourly rates (USD) — approximate Azure pay-as-you-go pricing.
# Not live pricing; sufficient for the MVP's cost estimation.
VM_HOURLY_RATES={
    "Standard_B1s":0.0104,
    "Standard_B2s":0.0416,
    "Standard_B2ms":0.0832,
    "Standard_B2ats_v2":0.0400,
    "Standard_D2s_v3":0.096,
    "Standard_D4s_v3":0.192,
}

DEFAULT_HOURLY_RATE:0.05
DEFAULT_HOURLY_RATE = 0.05  # fallback for unrecognized sizes

def estimate_monthly_spend(project:str) -> float:
    """
    Rough mock spend estimate: for each VM tagged with this project,
    assume it's been running since the start of the current month
    if it's currently 'running', otherwise assume 0 hours this month.
    """
    db=SessionLocal()
    try:
        resources=db.query(Resource).filter(Resource.project==project).all()
        now=datetime.now()
        days_elapsed=now.day
        hours_elapsed=days_elapsed*24

        total=0.0
        for r in resources:
            rate = VM_HOURLY_RATES.get(r.vm_size,DEFAULT_HOURLY_RATE)
            if r.power_state and "running" in r.power_state.lower():
                total+=rate*hours_elapsed
        return round(total,2)

    finally:
        db.close()

def get_budget_state(budget:dict, current_spend:float)->str:
    limit=budget["monthly_limit"]
    if limit<=0:
        return "normal"
    spend_ratio=(current_spend/float(limit))*100

    if spend_ratio>=budget["critical_threshold_percent"]:
        return "critical"
    elif spend_ratio>=budget["warning_threshold_percent"]:
        return "warning"
    return "normal"

def get_spend_summary()->list[dict]:
    budgets=get_all_budgets()
    summary=[]
    for b in budgets:
        spend=estimate_monthly_spend(b["project"])
        state=get_budget_state(b,spend)
        summary.append({
            "budget_id":b["id"],
            "project":b["project"],
            "monthly_limit":b["monthly_limit"],
            "current_spend":spend,
            "state":state,
        })

    return summary