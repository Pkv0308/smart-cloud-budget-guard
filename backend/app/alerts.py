from fastapi import APIRouter, HTTPException

from backend.app.schemas import AlertAckOut, AlertOut
from backend.app.services.alerts import acknowledge_alert, get_all_alerts

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/", response_model=list[AlertOut])
def get_alerts_route(acknowledged: bool | None = None):
    return get_all_alerts(acknowledged)


@router.post("/{alert_id}/acknowledge", response_model=AlertAckOut)
def acknowledge_alert_route(alert_id: int):
    result = acknowledge_alert(alert_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return result