from datetime import datetime, timedelta, timezone
from azure.identity import DefaultAzureCredential
from azure.mgmt.monitor import MonitorManagementClient
import os

from dotenv import load_dotenv

load_dotenv()

def get_cpu_percent(resource_id:str)->float | None:
    """Fetches Average CPU utilization for a VM over the last hour"""
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
