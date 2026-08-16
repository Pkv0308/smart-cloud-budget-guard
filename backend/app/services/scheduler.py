from apscheduler.schedulers.background import BackgroundScheduler
from backend.app.services.metrics import collect_and_store_metrics
from datetime import datetime
import logging

logging.basicConfig()
logging.getLogger("apscheduler").setLevel(logging.DEBUG)

scheduler=BackgroundScheduler()


def start_scheduler():
    scheduler.add_job(
        collect_and_store_metrics,
        "interval",
        hours=1,
        id="metrics_collection",
        next_run_time=datetime.now(),
    )
    scheduler.start()