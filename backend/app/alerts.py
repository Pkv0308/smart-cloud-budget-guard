from fastapi import APIRouter, HTTPException
from backend.app.services.alerts import get_all_alerts, acknowledge_alert

router=APIRouter(prefix='/alerts',tags=["alerts"])

@router.get("/")
def get_alerts_route(acknowledged:bool | None = None):
    return get_all_alerts(acknowledged)

@router.post("/{alert_id}/acknowledge")
def acknowledge_alert_route(alert_id:int):
    result=acknowledge_alert(alert_id)
    if result is None:
        return HTTPException(status_code=404, detail="Alert not found")
    return result