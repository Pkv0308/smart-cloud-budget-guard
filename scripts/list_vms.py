"""
Standalone script to list Azure VMs in the subscription.

This script uses Azure Identity (DefaultAzureCredential) and
Azure Compute Management SDK to list all virtual machines.

Prerequisites:
- Azure service principal or logged-in Azure CLI with sufficient permissions.
- Environment variables:
    - AZURE_SUBSCRIPTION_ID
"""

import os
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient


def list_vms()->None:
    """List all VMs in the configured Azure subscription and print basic info."""
    subscription_id=os.getenv("AZURE_SUBSCRIPTION_ID")
    if not subscription_id:
        raise RuntimeError(
            "AZURE_SUBSCRIPTION_ID environment variable is not set"
        )

    credential = DefaultAzureCredential()

    compute_client=ComputeManagementClient(credential,subscription_id)

    vms = compute_client.virtual_machines.list_all()
    print(f"Listing VMs in the subscription: {subscription_id}\n")
    for vm in vms:
        print(f"Name: {vm.name}")
        print(f"Location: {vm.location}")
        print(f"Power State: {vm.getattr(vm,'power_state','unknown')}")
        print(f"Tags: {vm.tags or {}}")
        print(f"-"*40)

if __name__=="__main__":
    list_vms()