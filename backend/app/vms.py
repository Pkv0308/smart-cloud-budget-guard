from fastapi import APIRouter
from scripts.list_vms import list_vms_data

router = APIRouter(prefix="/vms",tags=["vms"])

@router.get("/")
def list_vms_route():
    """Return Azure VM list and summary for SmartBudgetGuard."""
    data = list_vms_data()
    return data