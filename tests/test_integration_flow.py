from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import text

from backend.app.database import SessionLocal
from backend.app.database.models import (
    Alert,
    AutomationLog,
    Metric,
    Recommendation,
    Resource,
)
from backend.app.services.alerts import create_alert_from_idle_vms
from backend.app.services.automation import recommend
from backend.app.services.metrics import get_idle_vms

pytestmark = pytest.mark.integration

DEV_VM = "itest-dev-vm"
PROD_VM = "itest-prod-vm"
TEST_VMS = [DEV_VM, PROD_VM]


def _purge():
    """Delete every row this test creates. Only touches names starting 'itest-'."""
    with SessionLocal() as db:
        db.query(Alert).filter(Alert.vm_name.in_(TEST_VMS)).delete(synchronize_session=False)
        db.query(Recommendation).filter(Recommendation.vm_name.in_(TEST_VMS)).delete(synchronize_session=False)
        db.query(AutomationLog).filter(AutomationLog.vm_name.in_(TEST_VMS)).delete(synchronize_session=False)
        # metrics before resources: vm_metrics references resources(vm_name)
        db.query(Metric).filter(Metric.vm_name.in_(TEST_VMS)).delete(synchronize_session=False)
        db.query(Resource).filter(Resource.vm_name.in_(TEST_VMS)).delete(synchronize_session=False)
        db.commit()


@pytest.fixture
def seeded():
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except Exception:
        pytest.skip("PostgreSQL is not reachable")

    _purge()  # clear leftovers from any earlier crashed run

    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        db.add_all(
            [
                Resource(
                    vm_name=DEV_VM,
                    resource_id="/test/dev",
                    power_state="VM running",
                    environment="Development",
                    project="itest",
                    tags={"Environment": "Development", "AutoShutdown": "True"},
                ),
                Resource(
                    vm_name=PROD_VM,
                    resource_id="/test/prod",
                    power_state="VM running",
                    environment="Production",
                    project="itest",
                    tags={"Environment": "Production", "AutoShutdown": "False"},
                ),
            ]
        )
        db.commit()  # resources must exist before their metrics

        for name in TEST_VMS:
            db.add_all(
                [
                    Metric(vm_name=name, cpu_percent=1.0, network_in_bytes=100,
                           network_out_bytes=100, recorded_at=now - timedelta(minutes=90)),
                    Metric(vm_name=name, cpu_percent=0.8, network_in_bytes=100,
                           network_out_bytes=100, recorded_at=now - timedelta(minutes=20)),
                ]
            )
        db.commit()

    yield
    _purge()  # runs even if the test fails


def test_inventory_to_idle_to_alert_to_recommendation(seeded):
    # 1. idle detection picks up both seeded VMs
    idle = get_idle_vms()
    assert DEV_VM in idle
    assert PROD_VM in idle

    # 2. an alert is raised for each idle VM
    created = create_alert_from_idle_vms()
    assert created >= 2
    with SessionLocal() as db:
        alerted = {
            a.vm_name
            for a in db.query(Alert).filter(
                Alert.vm_name.in_(TEST_VMS), Alert.alert_type == "idle_vm"
            )
        }
    assert alerted == set(TEST_VMS)

    # 3. a second pass does not duplicate unacknowledged alerts
    create_alert_from_idle_vms()
    with SessionLocal() as db:
        count = (
            db.query(Alert)
            .filter(Alert.vm_name.in_(TEST_VMS), Alert.alert_type == "idle_vm")
            .count()
        )
    assert count == 2

    # 4. recommendations respect the safety gate: only the dev VM qualifies
    recommend()
    with SessionLocal() as db:
        recommended = {
            r.vm_name
            for r in db.query(Recommendation).filter(Recommendation.vm_name.in_(TEST_VMS))
        }
    assert recommended == {DEV_VM}