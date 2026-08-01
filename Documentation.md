# Documentation
### This file serves as a record of the development journey of the project. It will be updated as a session logs which indicate the tasks performed on a specific date.
<hr>

## Session Logs

### 27 July 2026
 - Initialized the repository
 - Prepared the README documenation.

### 29 July 2026
 - Installed python environment
 - Installation and testing of project dependencies.

### 31 July 2026
 - Created initial FastAPI app structure
 - Verified the FastAPI server runs locally, including the endpoints
 - Created an initial Azure VM listing script

### 1 August 2026
 - Azure CLI installation
 - refactored list_vms.py to bypass .env credentials and use Azure CLI credentials
 - list_vms.py now provides structured summary in CLI
 - verified listing of vms in the azure account logged in via the CLI
 - updated module imports in vms.py
 - vms.py now returns current VM data in JSON