from azure.core.exceptions import ClientAuthenticationError
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from backend.app.main import app

# No "with" block on purpose: that would run the lifespan and start the scheduler.
client = TestClient(app)


# ---------- basics ----------

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["service"] == "Smart Budget Guard"


# ---------- request validation ----------

def test_budget_negative_limit_is_rejected_with_readable_message():
    r = client.post("/budgets/", json={"project": "Test", "monthly_limit": -5})
    assert r.status_code == 422
    assert "monthly_limit" in r.json()["detail"]


def test_budget_missing_project_is_rejected():
    r = client.post("/budgets/", json={"monthly_limit": 50})
    assert r.status_code == 422
    assert "project" in r.json()["detail"]


# ---------- alerts ----------

def test_alerts_list_is_serialised(monkeypatch):
    fake = [
        {
            "id": 1,
            "alert_type": "idle_vm",
            "vm_name": "vm1",
            "budget_id": None,
            "severity": "warning",
            "message": "idle",
            "acknowledged": False,
            "created_at": "2026-11-03T10:00:00",
        }
    ]
    monkeypatch.setattr("backend.app.alerts.get_all_alerts", lambda acknowledged=None: fake)
    r = client.get("/alerts/")
    assert r.status_code == 200
    assert r.json() == fake


def test_alerts_filter_is_passed_through(monkeypatch):
    seen = {}

    def fake(acknowledged=None):
        seen["value"] = acknowledged
        return []

    monkeypatch.setattr("backend.app.alerts.get_all_alerts", fake)
    client.get("/alerts/?acknowledged=false")
    assert seen["value"] is False


def test_acknowledge_unknown_alert_returns_404(monkeypatch):
    monkeypatch.setattr("backend.app.alerts.acknowledge_alert", lambda alert_id: None)
    r = client.post("/alerts/999/acknowledge")
    assert r.status_code == 404
    assert r.json() == {"detail": "Alert not found"}


# ---------- automation safety ----------

def test_automation_run_defaults_to_dry_run(monkeypatch):
    seen = {}

    def fake_run(vm_name, dry_run):
        seen["args"] = (vm_name, dry_run)
        return {"vm_name": vm_name, "result": "dry_run_success", "detail": "x"}

    monkeypatch.setattr("backend.app.automation.run_automation", fake_run)
    r = client.post("/automation/run", json={"vm_name": "vm1"})
    assert r.status_code == 200
    assert seen["args"] == ("vm1", True)


def test_automation_run_passes_explicit_live_flag(monkeypatch):
    seen = {}

    def fake_run(vm_name, dry_run):
        seen["args"] = (vm_name, dry_run)
        return {"vm_name": vm_name, "result": "success", "detail": "x"}

    monkeypatch.setattr("backend.app.automation.run_automation", fake_run)
    client.post("/automation/run", json={"vm_name": "vm1", "dry_run": False})
    assert seen["args"] == ("vm1", False)


# ---------- central error handling ----------

def test_database_error_returns_503(monkeypatch):
    def boom(acknowledged=None):
        raise SQLAlchemyError("db down")

    monkeypatch.setattr("backend.app.alerts.get_all_alerts", boom)
    r = client.get("/alerts/")
    assert r.status_code == 503
    assert "PostgreSQL" in r.json()["detail"]


def test_azure_auth_error_returns_502(monkeypatch):
    def boom():
        raise ClientAuthenticationError("not logged in")

    monkeypatch.setattr("backend.app.vms.sync_inventory", boom)
    r = client.post("/vms/sync")
    assert r.status_code == 502
    assert "az login" in r.json()["detail"]


def test_unexpected_error_returns_500_json(monkeypatch):
    def boom():
        raise ValueError("surprise")

    monkeypatch.setattr("backend.app.vms.get_idle_vms", boom)
    r = client.get("/vms/idle")
    assert r.status_code == 500
    assert "detail" in r.json()