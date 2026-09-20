from backend.app.database import SessionLocal
from backend.app.database.models import Resource, Recommendation, AutomationLog
from backend.app.services.metrics import get_idle_vms
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
import os
from dotenv import load_dotenv

load_dotenv()

def is_automation_eligible(resource:Resource)->bool:
    """
    Hard safety gate: a VM is only eligible for automated action if it is
    explicitly tagged Environment=Development AND AutoShutdown=True.
    Anything else — including missing tags — is excluded by default.
    """
    tags=resource.tags or []
    environment=tags.get("Environment","")
    auto_shutdown=tags.get("AutoShutdown","")

    return(
        environment.strip().lower()=="development" and str(auto_shutdown).strip().lower()=='true'
    )

def recommend()->list[dict]:
    """
    Cross-reference idle VMs against the automation safety gate, and
    persist a recommendation for each eligible idle VM.
    """
    db=SessionLocal()
    try:
        idle_vms=get_idle_vms()
        if not idle_vms:
            return
        resources=db.query(Resource).filter(Resource.vm_name.in_(idle_vms)).all()
        results=[]

        for r in resources:
            if not is_automation_eligible(r):
                continue
            existing=db.query(Recommendation).filter(
                Recommendation.vm_name==r.vm_name,
                Recommendation.status=="pending"
            ).first()
            if existing:
                results.append({"vm_name":r.vm_name, "status":"already_pending"})
                continue

            rec=Recommendation(
                vm_name=r.vm_name,
                reason="Idle for 2+ hours (CPU < 5%, network < 5 KB/s) and tagged for automated shutdown."
            )
            db.add(rec)
            db.commit()
            db.refresh(rec)

            log_entry=AutomationLog(
                vm_name=r.vm_name,
                action="recommend",
                dry_run=True,
                result="success",
                detail=rec.reason,
            )

            db.add(log_entry)
            db.commit()

            results.append({"vm_name":r.vm_name, "status":"recommended","recommendation_id":rec.id})

        return results
    finally:
        db.close()

def get_automation_logs()->list[dict]:
    db=SessionLocal()
    try:
        logs=db.query(AutomationLog).order_by(AutomationLog.created_at.desc()).all()
        return [
            {
                "id":log.id,
                "vm_name":log.vm_name,
                "action":log.action,
                "dry_run":log.dry_run,
                "result":log.result,
                "detail":log.detail,
                "created_at":log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ]
    finally:
        db.close()

def run_automation(vm_name:str, dry_run:bool = True) ->dict:
    """
    Execute (or simulate) a stop action for a VM with a pending recommendation.
    Re-validates eligibility at execution time — never trusts a stale recommendation alone.
    """
    db=SessionLocal()
    try:
        resource=db.query(Resource).filter(Resource.vm_name==vm_name).first()
        if not resource:
            return {"vm_name":vm_name," result":"error","detail":"VM not found in inventory"}

        if not is_automation_eligible(resource):
            log_entry=AutomationLog(
                vm_name=vm_name, action="stop", dry_run=dry_run,
                result="skipped",detail="Faield safety gate at execution time"
            )
            db.add(log_entry)
            db.commit()
            return {
                "vm_name":vm_name,
                "result":"skipped",
                "detail":"Not elgigible for Automation"
            }

        if dry_run:
            detail="Dry Run \u2014 no action taken. This VM would have been stopped."
            log_entry=AutomationLog(
                vm_name=vm_name, action="stop",dry_run=True,
                result="success",detail=detail
            )

            db.add(log_entry)
            db.commit()
            return{
                "vm_name":vm_name,
                "result":"dry_run_success",
                "detail":detail
            }

        #-----------------------------------
        #------------REAL-STOP--------------
        #-----------------------------------

        subscription_id=os.getenv("AZURE_SUBSCRIPTION_ID")
        credential=DefaultAzureCredential(
            exclude_environment_credential=True,
            exclude_managed_identity_credential=True,
            exclude_shared_token_cache_credential=True,
            exclude_visual_studio_code_credential=False,
            exclude_azure_cli_credential=False
        )
        compute_client=ComputeManagementClient(credential,subscription_id)
        parts=resource.resource_id.split("/")
        rg_name=parts[4]

        try:
            compute_client.virtual_machine.begin_deallocate(rg_name,vm_name)
            detail="VM stop initiated."
            result="success"
        except Exception as e:
            detail = f"Error Stopping VM: {str(e)}"
            result="error"

        log_entry=AutomationLog(
            vm_name=vm_name,
            action="stop",
            dry_run=False,
            result=result,
            detail=detail
        )
        db.add(log_entry)
        db.commit
        return{
            "vm_name":vm_name,
            "result":result,
            "detail":detail
        }

    finally:
        db.close()