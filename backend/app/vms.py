from fastapi import APIRouter

router = APIRouter(prefix="/vms",tags=["vms"])

@router.get("/")
def list_vms_stub():
    return {
        "message":"VM listing not implemented yet",
        "data":[]
    }