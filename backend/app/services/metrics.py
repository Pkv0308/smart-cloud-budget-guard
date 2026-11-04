from datetime import datetime, timedelta, timezone
from azure.identity import DefaultAzureCredential
from azure.mgmt.monitor import MonitorManagementClient
from backend.app.database import SessionLocal
from backend.app. database.models import Resource,Metric
from sqlalchemy import select
import os
import logging
from azure.core.exceptions import ResourceNotFoundError

logger = logging.getLogger("smart_budget_guard.metrics")
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


def collect_and_store_metrics() -> dict:
    """
    Fetch CPU + network metrics for every VM in inventory and persist a row per VM.
    A failure for one VM is logged and skipped; it never stops the others.
    """
    db = SessionLocal()
    try:
        resources = db.query(Resource).all()
        collected = 0
        failed = 0
        for r in resources:
            if not r.resource_id:
                continue
            try:
                cpu = get_cpu_percent(r.resource_id)
                net = get_network_bytes(r.resource_id)
            except ResourceNotFoundError:
                logger.warning(
                    "Metrics skipped for '%s': resource no longer exists in Azure.",
                    r.vm_name,
                )
                failed += 1
                continue
            except Exception:
                logger.exception("Metrics fetch failed for '%s'", r.vm_name)
                failed += 1
                continue

            db.add(
                Metric(
                    vm_name=r.vm_name,
                    cpu_percent=cpu,
                    network_in_bytes=net["network_in_bytes"],
                    network_out_bytes=net["network_out_bytes"],
                )
            )
            collected += 1
        db.commit()
        return {"collected": collected, "failed": failed}
    finally:
        db.close()

CPU_IDLE_THRESHOLD_PERCENT = 5.0
NETWORK_IDLE_THRESHOLD_BYTES_PER_SEC = 5 * 1024  # ~3x the observed Azure background baseline
COLLECTION_INTERVAL_SECONDS = 3600  # each sample covers one hourly collection
IDLE_WINDOW_HOURS = 2
MIN_SAMPLES = 2


def is_idle(samples) -> bool:
    """
    Idle only if there are enough samples and EVERY sample is below both the
    CPU threshold and the (interval-scaled) network threshold.
    Each sample needs cpu_percent, network_in_bytes and network_out_bytes.
    """
    samples = list(samples)
    if len(samples) < MIN_SAMPLES:
        return False

    network_limit = NETWORK_IDLE_THRESHOLD_BYTES_PER_SEC * COLLECTION_INTERVAL_SECONDS
    return all(
        s.cpu_percent is not None
        and s.cpu_percent < CPU_IDLE_THRESHOLD_PERCENT
        and (s.network_in_bytes or 0) + (s.network_out_bytes or 0) < network_limit
        for s in samples
    )


def get_idle_vms() -> list[str]:
    """Return names of VMs whose samples in the last IDLE_WINDOW_HOURS are all idle."""
    db = SessionLocal()
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=IDLE_WINDOW_HOURS)
        rows = db.execute(
            select(Metric).where(Metric.recorded_at >= cutoff)
        ).scalars().all()

        by_vm: dict[str, list] = {}
        for row in rows:
            by_vm.setdefault(row.vm_name, []).append(row)

        return [vm_name for vm_name, samples in by_vm.items() if is_idle(samples)]
    finally:
        db.close()