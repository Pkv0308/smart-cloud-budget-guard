import logging
from datetime import datetime
from backend.app.services.vm_inventory import sync_inventory

from apscheduler.schedulers.background import BackgroundScheduler

from backend.app.services.alerts import (
    create_alert_from_budget_states,
    create_alert_from_idle_vms,
)
from backend.app.services.automation import recommend
from backend.app.services.metrics import collect_and_store_metrics

logger = logging.getLogger("smart_budget_guard.scheduler")

scheduler = BackgroundScheduler()


def run_monitoring_cycle():
    """One full pass: collect metrics, raise alerts, then generate recommendations."""
    steps = [
        ("sync inventory", sync_inventory),
        ("collect metrics", collect_and_store_metrics),
        ("idle alerts", create_alert_from_idle_vms),
        ("budget alerts", create_alert_from_budget_states),
        ("recommendations", recommend),
    ]
    for name, step in steps:
        try:
            result = step()
            logger.info("Monitoring cycle - %s: done (%s)", name, result)
        except Exception:
            logger.exception("Monitoring cycle - %s failed", name)


def start_scheduler():
    scheduler.add_job(
        run_monitoring_cycle,
        "interval",
        hours=1,
        id="monitoring_cycle",
        next_run_time=datetime.now(),
    )
    scheduler.start()