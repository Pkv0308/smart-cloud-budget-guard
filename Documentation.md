# Documentation

This file is the record of the development journey of the project. It is updated
as a session log — one dated entry per work session, describing what was done.

## Session Logs

### 27 July 2026
**Summary:** Repository initialized.
- Initialized the repository.
- Prepared the initial README documentation.

### 29 July 2026
**Summary:** Local environment set up.
- Installed the Python environment.
- Installed and tested project dependencies.

### 31 July 2026
**Summary:** Initial FastAPI app and Azure VM listing script created.
- Created the initial FastAPI app structure.
- Verified the FastAPI server runs locally, including the endpoints.
- Created an initial Azure VM listing script.

### 1 August 2026
**Summary:** Auth switched to Azure CLI credentials; VM listing returns structured data.
- Installed Azure CLI.
- Refactored `list_vms.py` to bypass `.env`-based credentials and use Azure CLI
  credentials instead 
- `list_vms.py` now provides a structured summary in the CLI.
- Verified VM listing against the Azure account logged in via the CLI.
- Updated module imports in `vms.py`.
- `vms.py` now returns current VM data as JSON.

<!-- ### 2 August 2026
**Summary:** Project structure verified end-to-end; skeleton confirmed stable; core documents finalized.
- Verified the full project tree (`backend/app/` containing `main.py`, `vms.py`,
  `__init__.py`; `scripts/` containing `list_vms.py`).
- Confirmed that `from backend.app.vms import router` and
  `from scripts.list_vms import list_vms_data` resolve correctly when `uvicorn`
  is run from the project root — no import fix was needed.
- Noted `scripts/` is missing an `__init__.py`; works via CWD-based path
  resolution but should be added for explicitness.
- Finalized `README.md`: single tech-stack decision per layer, MVP scope only.
- Finalized `developmentPlan.md`: 11-week plan broken into daily 2-hour sessions
  (paced for ~2 hours/day), with an explicit scope-cut order if behind schedule.
- Finalized `requirements.txt`: trimmed to MVP dependencies (FastAPI, Azure SDK,
  SQLAlchemy + psycopg2, APScheduler, python-dotenv); testing and config-management
  packages deferred to the weeks that actually need them.
- **Week 1 checkpoint reached.** Ready to begin Week 2 (PostgreSQL persistence). -->