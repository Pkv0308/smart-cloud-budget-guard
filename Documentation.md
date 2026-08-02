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

### 2 August 2026
**Summary:** PostgreSQL installation and schema applied, Updated DB driver due to python 3.14 incompatibility
- Installed Postgres, created database and table successfully
- switched from psycopg2-binary to psycopg(v3) due to python3.14 incompatibility
- confirmed successful database conenction