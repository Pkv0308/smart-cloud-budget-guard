from datetime import datetime, timedelta, timezone
from azure.identity import DefaultAzureCredential
from azure.mgmt.monitor import MonitorManagementClient
from backend.app.database import SessionLocal
from backend.app. database.models import Resource,Metric
from sqlalchemy import select
import os

from dotenv import load_dotenv

load_dotenv()
subscription_id=os.getenv("AZURE_SUBSCRIPTION_ID")
credential=DefaultAzureCredential(
        exclude_environment_credential=True,
        exclude_managed_identity_credential=True,
        exclude_shared_token_cache_credential=True,
        exclude_visual_studio_code_credential=False,
        exclude_azure_cli_credential=False,
    )

client=MonitorManagementClient(credential,subscription_id)

end_time=datetime.now(timezone.utc)

start_time= end_time - timedelta(hours=1)

timespan = f"{start_time.strftime('%Y-%m-%dT%H:%M:%SZ')}/{end_time.strftime('%Y-%m-%dT%H:%M:%SZ')}"

def get_cpu_percent(resource_id:str)->float | None:
    """Fetches Average CPU utilization for a VM over the last hour"""

    metrics_data=client.metrics.list(
        resource_id,
        timespan=timespan,
        interval="PT1H",
        metricnames="Percentage CPU",
        aggregation="Average",
    )

    for item in metrics_data.value:
        for ts in item.timeseries:
            for data in ts.data:
                if data.average is not None:
                    return round(data.average,2)

    return None

def get_network_bytes(resource_id : str)-> dict:
    """Fetch total network in/out bytes for a VM over the last hour"""

    metrics_data=client.metrics.list(
        resource_id,
        timespan=timespan,
        interval="PT1H",
        metricnames="Network In Total,Network Out Total",
        aggregation="Total",
    )


    result = {"network_in_bytes":None, "network_out_bytes":None}
    for item in metrics_data.value:
        for ts in item.timeseries:
            for data in ts.data:
                if data.total is not None:
                    if item.name.value=="Network In Total":
                        result["network_in_bytes"]=data.total
                    elif item.name.value=="Network Out Total":
                        result['network_out_bytes']=data.total

    return result


def collect_and_store_metrics() -> int:
    """Fetch CPU + Network metric for every VM in inventory and persist a row per VM"""
    db=SessionLocal()
    try:
        resources=db.query(Resource).all()
        count=0
        for r in resources:
            if not r.resource_id:
                continue
            cpu=get_cpu_percent(r.resource_id)
            network=get_network_bytes(r.resource_id)
            metric=Metric(
                vm_name=r.vm_name,
                cpu_percent=cpu,
                network_in_bytes=network["network_in_bytes"],
                network_out_bytes=network["network_out_bytes"],
            )
            db.add(metric)
            count+=1
        db.commit()
        return count
    finally:
        db.close()

def get_idle_vms() -> list[str]:
    """
    Return vm_names whose metrics over the last 2 hours are all below the
    idle thresholds: CPU < 5% and (network_in + network_out) < 1 KB/s equivalent.
    """

    db=SessionLocal()
    try:
        cutoff=datetime.now(timezone.utc) - timedelta(hours=2)
        rows=db.execute(select(Metric).where(Metric.recorded_at>=cutoff)).scalars().all()

        by_vm :dict[str,list[Metric]]={}
        for row in rows:
            by_vm.setdefault(row.vm_name,[]).append(row)

        idle_vms=[]
        for vm_name, metrics in by_vm.items():
            if len(metrics)<2:
                continue
            all_below_threshold=all(
                (m.cpu_percent is not None and m.cpu_percent<5.0) and ((m.network_in_bytes or 0) + (m.network_out_bytes or 0))<1024
                for m in metrics
            )

            if all_below_threshold:
                idle_vms.append(vm_name)

        return idle_vms
    finally:
        db.close()