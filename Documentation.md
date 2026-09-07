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

### 6 August 2026

**Summary:** Resources model and inventory upsert logic written and tested

- defined the Resource SQLAlchemy model
- implemented resource upsert logic, updates on conflict
- tested the upsert script against real Azure data
- update logic for "VM Deallocated" state
- added `/sync` route that fetches data from Azure and upserts into DB
- added `/vms/inventory` that returns persisted data from DB

### 9 August 2026

**Summary:** scripted VM Metric (Percentage CPU) collection, added persistence of Azure resource id into resources

- added vm_metrics table in schema and Metric model in models
- added resource_id to Resources and updated across `list_vms`, `models`, `vm_inventory`
- scripted `metrics.py` to get average CPU utilization percentage over the last hour
- tested metrics against deallocated VM and running VM

### 13 August 2026

**Summary:** Added network metric collection, persisted metric data (CPU +  network in/out) to DB

- udpated `metrics.py` to return VM network usage
- tested and verified network functionality againt live VM, returning network in/out bytes
- added metrics persistence mechanism, stores a row per VM
- tested and verified per VM metric persistence into the DB

### 15 August 2026 - Happy Independence Day

**Summary:** implemented scheduler to retrieve hourly VM metrics, idle detection rule implemented and confirmed working

- implemented `start_scheduler()` into FastAPI's startup event
- `collect_and_store_metrics()` now runs hourly when the backend is on
- scheduler confirmed working at regular intervals (tested for per minute retrieval)
- scripted `get_idle_vms()` that returns idle VMs from last 2 hours with conditions CPU<5% and network<1KB
- tested and verified idle VM retrieval by inserting sample data

### 16 August 2026

**Summary:** migrated from deprecated @app.on_event to lifespan async context manager, fine tuned the idle threshold

- replaced the deprecated `@app.on_event("startup")` with `lifespan async context manager`
- added scheduler logging functionality for easy debug
- network threshold was previously compared against hourly total, corrected by scaling to per second rates
- tuned threshold to CPU<5% and network<5KB/s (an entirely idle Azure VM takes around 1.75KB/s which was not categorized as idle)
- confirmed the working of new thresholds

### 4 September 2026

**Summary:** implemented the budget engine using mock pricing and thresholds

- added `budgets` table to `db_schema.sql` and `Budget` model to `models.py`
- wrote `backend/app/services/budgets.py` with `create_budget()` and `get_all_budgets()`
- added `backend/app/budgets.py` router with `POST /budgets/` and `GET /budgets/`, registered in main.py
- created and retrieved a budget successfully
- hardcoded `VM_HOURLY_RATES` mock rate table with a fallback mechanism
- added `vm_size` column to `resources` and updated `list_vms, vm_inventory and models`
- confirmed vm_size persists in database

### 5 September 2026

**Summary:** implemented budget update mechanism and mock spend estimation with budget state

- added `update_budget()` to `budgets.py1` and `PUT /bugets/{id}` route
- tested and verified updating monthly limit on an existing budget
- implemented `estimate_monthly_spend()` that estimates monthly spend for a running VM (assumes continuous runtime since day 1 of month; `not real billing`)
- categorized budget spend using `get_budget_state` based on spend-to-limit ratio
- added `get_spend_summary` that summarize budgets across VMs
- implemented `GET /budgets/spend` route, tested and verified

### 7 September 2026

**Summary:** implemented alert system for idle VMs and budget threshold

- added `alerts` table and the `Alerts` model
- wrote `backend/app/services/alerts.py`
- implemented alert creation functionality: manual, idle VMs and budget states
- tested and verified alert creation of idle VMs and budget overflow
- alert listing and acknowledge endpoints added
- testing alert listing, acknowledged filtering (false and true)
