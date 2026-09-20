import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("smart_budget_guard.notifications")

def notify(message:str, severity:str = "info") ->None:
    """Console/log notification path"""
    if severity=="critical":
        logger.error(f"[CRITICAL] {message}")
    elif severity == "warning":
        logger.warning(f"[WARNING] {message}")
    else:
        logger.info(f"[INFO] {message}")