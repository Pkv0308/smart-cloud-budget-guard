from fastapi import APIRouter

from backend.app.schemas import IdleVmsOut, ResourceOut, SyncOut
from backend.app.services.metrics import get_idle_vms
from backend.app.services.vm_inventory import get_all_resources, sync_inventory
from scripts.list_vms import list_vms_data

router = APIRouter(prefix="/vms", tags=["vms"])


@router.get("/")
def list_vms_route():
    """Return live Azure VM list and summary (bypasses the database)."""
    return list_vms_data()


@router.post("/sync", response_model=SyncOut)
def sync_vms_route():
    """Fetch VMs from Azure and persist them to the database."""
    return {"synced": sync_inventory()}


@router.get("/inventory", response_model=list[ResourceOut])
def get_inventory_route():
    """Return persisted VM inventory from the database."""
    return get_all_resources()


@router.get("/idle", response_model=IdleVmsOut)
def get_idle_vms_route():
    """Return VM names currently flagged as idle."""
    return {"idle_vms": get_idle_vms()}