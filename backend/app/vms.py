from fastapi import APIRouter
from scripts.list_vms import list_vms_data
from backend.app. services.vm_inventory import upsert_resources,get_all_resources

router = APIRouter(prefix="/vms",tags=["vms"])

@router.get("/")
def list_vms_route():
    """Return Azure VM list and summary for SmartBudgetGuard."""
    data = list_vms_data()
    return data

@router.get("/sync")
def sync_vms_route():
    """Fetch VMs from Azure and persist them to the database"""
    data=list_vms_data()
    count=upsert_resources(data["items"])
    return {"Synced: ": count}

@router.get("/inventory")
def get_inventory_route():
    """Returns persisted VM data from the database"""
    return get_all_resources()