"""
Standalone script to list Azure VMs in the subscription.

This script uses Azure Identity (DefaultAzureCredential) and
Azure Compute Management SDK to list all virtual machines.

Prerequisites:
- Azure service principal or logged-in Azure CLI with sufficient permissions.
- Environment variables:
    - AZURE_SUBSCRIPTION_ID
"""

from azure.core.exceptions import HttpResponseError
from azure.mgmt.compute import ComputeManagementClient
from azure.identity import DefaultAzureCredential
import os
from dotenv import load_dotenv
load_dotenv()


def list_vms_data() -> dict:
    """Return VM list and a tag-based summary for the subscription"""
    subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
    if not subscription_id:
        raise RuntimeError(
            "AZURE_SUBSCRIPTION_ID environment variable is not set"
        )

    """ Exclude environment credentials to avoid conflicts with shared machine env vars
              used Azure CLI / VS Code for local auth.
          """
    credential = DefaultAzureCredential(
        exclude_environment_credential=True,
        exclude_managed_identity_credential=True,
        exclude_shared_token_cache_credential=True,
        exclude_visual_studio_code_credential=False,
        exclude_azure_cli_credential=False,
    )

    compute_client = ComputeManagementClient(credential, subscription_id)
    vms_iter = compute_client.virtual_machines.list_all()

    vms = compute_client.virtual_machines.list_all()

    items: list[dict] = []
    summary : dict[tuple[str, str, str], dict[str, int]] = {}

    # print(f"Listing VMs in the subscription: {subscription_id}\n")
    for vm in vms_iter:
        # Try to get power state from instance view
        power_state = "unknown"

        try:
            parts = vm.id.split("/")
            rg_name = parts[4]  # /subscriptions/<sub>/resourceGroups/<rg>/...
            iv = compute_client.virtual_machines.instance_view(
                rg_name, vm.name)
            statuses = iv.statuses or []
            for s in statuses:
                if s.code.startswith("PowerState/"):
                    power_state = s.display_status  # e.g. "VM running"
                    break
        except HttpResponseError:
            power_state = "error"
        except Exception:
            power_state = "unknown"

        tags = vm.tags or {}

        project = tags.get("Project", "Unknown")
        owner = tags.get("Owner", "Unknown")
        env = tags.get("Environment", "Unknown")

        item = {
            "name": vm.name,
            "location": vm.location,
            "power_state": power_state,
            "tags": tags,
        }

        items.append(item)

        key = (project, owner, env)
        if key not in summary:
            summary[key] = {"running": 0, "stopped": 0, "unknown": 0, "error": 0}
        ps_lower = power_state.lower()
        if ps_lower.startswith("vm running"):
            summary[key]["running"] += 1
        elif ps_lower.startswith("vm stopped"):
            summary[key]["stopped"] += 1
        elif ps_lower == "error":
            summary[key]["error"] += 1
        else:
            summary[key]["unknown"] += 1

    summary_list : list[dict] = []

    for (project, owner, env), counts in summary.items():
        summary_list.append(
            {
                "project": project,
                "owner": owner,
                "environment": env,
                "running": counts["running"],
                "stopped": counts["stopped"],
                "unknown": counts["unknown"],
                "error": counts["error"],
            }
        )

    return {
        "subscription_id": subscription_id,
        "items": items,
        "summary": summary_list,
    }


def list_vms() -> None:
    """CLI helper: print VM list and summary to the console."""
    data = list_vms_data()
    print(f"Listing VMs in the subscription: {data['subscription_id']}\n")
    for vm in data["items"]:
        print(f"Name: {vm['name']}")
        print(f"Location: {vm['location']}")
        print(f"Power State: {vm['power_state']}")
        print(f"Tags: {vm['tags']}")
        print("-"*40)

    print("\nSummary by Project / Owner / Environment:\n")
    for (project, owner, env), counts in data["summary"].items():
        print(
            f"Project={project}, Owner={owner}, Environment={env} "
            f"=> running={counts['running']}, stopped={counts['stopped']}, "
            f"unknown={counts['unknown']}, error={counts['error']}"
        )


if __name__ == "__main__":
    list_vms()
