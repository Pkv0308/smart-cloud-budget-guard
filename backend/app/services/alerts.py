from backend.app.database.models import Alert
from backend.app.database import SessionLocal
from backend.app.services.metrics import get_idle_vms
from backend.app.services.cost_estimator import get_spend_summary

def create_alert(alert_type:str, severity:str, message:str, vm_name:str = None, budget_id:int = None)->dict:
    db=SessionLocal()
    try:
        alert=Alert(
            alert_type=alert_type,
            vm_name=vm_name,
            budget_id=budget_id,
            severity=severity,
            message=message,
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return{
            "id":alert.id,
            "alert_type":alert.alert_type,
            "message":alert.message
        }
    finally:
        db.close()

def create_alert_from_idle_vms()->int:
    """Check current idle VMs and create an alert for each, avoiding duplicates."""
    db=SessionLocal()
    try:
        idle_vms=get_idle_vms()
        count=0
        for vm_name in idle_vms:
            existing=db.query(Alert).filter(
                Alert.alert_type=="idle_vm",
                Alert.vm_name==vm_name,
                Alert.acknowledged==False
            ).first()
            if existing:
                continue
            create_alert(
                alert_type="idle_vm",
                severity="warning",
                message=f"VM {vm_name} has been idle for 2+ hours",
                vm_name=vm_name,
            )
            count+=1
        return count
    finally:
        db.close()

def create_alert_from_budget_states()->int:
    """Check current budget states and create an alert for warning/critical, avoiding duplicates."""
    db=SessionLocal()
    try:
        summary=get_spend_summary()
        count=0
        for b in summary:
            if b["state"]=="normal":
                continue
            existing=db.query(Alert).filter(
                Alert.alert_type=="budget_breach",
                Alert.budget_id==b["budget_id"],
                Alert.acknowledged==False,
            ).first()
            if existing:
                continue
            create_alert(
                alert_type="budget_breach",
                severity=b["state"],
                message=f"Budget for '{b['project']}' is at {b['state']} (${b['current_spend']} / ${b['monthly_limit']}).",
                budget_id=b["budget_id"],                
            )
            count+=1
        return count
    finally:
        db.close()

def get_all_alerts(acknowledged:bool=None)->list[dict]:
    db=SessionLocal()
    try:
        query=db.query(Alert)
        if acknowledged is not None:
            query=query.filter(Alert.acknowledged==acknowledged)
        alerts=query.order_by(Alert.created_at.desc()).all()
        return[
            {
                "id":a.id,
                "alert_type":a.alert_type,
                "vm_name":a.vm_name,
                "budget_id":a.budget_id,
                "severity":a.severity,
                "message":a.message,
                "acknowledged":a.acknowledged,
                "created_at":a.created_at.isoformat() if a.created_at else None,
            }
            for a in alerts
        ]
    finally:
        db.close()

def acknowledge_alert(alert_id:int) ->dict | None:
    db=SessionLocal()
    try:
        alert=db.query(Alert).filter(Alert.id==alert_id).first()
        if not alert:
            return None
        alert.acknowledged=True
        db.commit()
        db.refresh(alert)
        return{
            "id":alert.id,
            "acknowledged":alert.acknowledged
        }
    finally:
        db.close()