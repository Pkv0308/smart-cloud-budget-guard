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

### 19 September 2026

**Summary** implemented notification functionality, recommendations, automation

- added console/log notification mechanism so every new alert (idle or buidget) triggers a notification automatically
- created recommendations and automation_logs tables and models
- implemented safety mechanism to identify VM for automation eligible, tested and verified
- gathers automation eligible VM and persists into database preventing duplicates

### 20 September 2026

**Summary:** recommend and logs endpoint added; implented dry-run functionality

- updated automation to write an automation log every time a VM is recommended, creating a full audit trail
- added automation router with POST and GET requests
- tested and verified these endpoints
- implemented dry-run functionality for VM termination, validates eligibility at execution time
- added POST dry-run endpoint
- tested and verified dry-run funtionality

### 5 October 2026

**Summary:** implemented frontend MVP

- Scaffolded a React + Vite frontend in `frontend/`, connected to the FastAPI backend (CORS enabled).
- Added a central API client wrapping every backend endpoint.
- **VMs page:** persisted inventory with power state, tags, and an idle indicator, filterable by environment, auto-shutdown, and idle state.
- **Overview page:** alert counts (active, critical, warning, acknowledged) and budget cards showing spend against limit.
- Alerts and Automation pages are placeholders, planned for Week 8.

### 25 October 2026 

**Summary:** Frontend completed (Alerts page, Automation page, charts, loading and error handling) and the scheduler now runs the full monitoring cycle. Week 8 checkpoint met.

- Built the Alerts page (`Alerts.jsx`)
- Built the Automation page (`Automation.jsx`)
- Added `GET /automation/recommendations`  and `getRecommendations` in `api.js`
- Fixed a bug where `POST /automation/recommend` returned `null` when no VMs were idle, which crashed the page. Every code path now returns a list.
- Added Overview charts with Recharts (`components/Charts.jsx`): VMs by state and spend vs limit
- Made loading and error handling consistent across all four pages: friendlier API errors
- Replaced the hourly scheduled job with `run_monitoring_cycle()` (collect metrics, idle alerts, budget alerts, recommendations)
- Confirmed the scheduler: metric collection fails for the deleted VM (expected), but the remaining steps still ran and an idle alert was created from test metric rows without any manual call.

### 3 November 2026 
**Summary:** Backend hardened and an automated test suite added.
- Metric collection now isolates failures per VM: a VM deleted in Azure is skipped with a single warning, other failures are logged, and the remaining VMs are still collected. The Azure SDK already retries transient errors, so no custom retry loop was written.
- Inventory sync is now the first step of the hourly monitoring cycle, so power state, tags, and the VM list refresh automatically instead of only on a manual `POST /vms/sync`.
- Added central error handling (`errors.py`) that keeps the existing `{"detail": "..."}` shape: readable validation errors (422), Azure failures (502), database errors (503), and a catch-all for unexpected errors (500). The catch-all is registered before the CORS middleware so the browser can still read its responses.
- Added Pydantic response schemas (`schemas.py`) for the main endpoints and tightened budget request validation (limit above zero, thresholds between 0 and 100, non-empty project). Wiring mistakes found while applying this (an undefined `router` in `automation.py`, `POST /budgets/` reading its fields from the query string, and stacked decorators in `vms.py`) were fixed by replacing the route files with complete versions.
- Added a pytest suite of 46 tests: 15 for the automation safety gate, 9 for budget state, 10 for the idle rule (extracted into a pure `is_idle()` function), and 12 API tests that use fake services, so they need neither PostgreSQL nor Azure.
- The tests caught two real bugs: `is_automation_eligible()` crashed on VMs with empty or missing tags, so any non-dict tags value is now ineligible, and `POST /automation/run` was not reaching its handler, which was corrected.
- Findings: with the database unreachable the UI waited minutes before showing an error because the engine had no connection timeout (fix: `connect_timeout` and `pool_timeout`), and sync does not remove VMs deleted in Azure, since the live listing was empty while the database still held the old row.

### 4 November 2026 
**Summary:** End-to-end integration test added; Week 9 checkpoint met. 47 tests passing.
- Added `pytest.ini` with an `integration` marker and one integration test against the real PostgreSQL. It seeds two idle VMs (one `Development` with `AutoShutdown=True`, one `Production`) and checks that both are flagged idle and alerted, that a second pass creates no duplicate alerts, and that only the development VM is recommended. Its fixture removes its own `itest-` rows before and after, and the test is skipped if the database is unreachable.
- Verified the suite catches regressions: forcing the safety gate to always return `True` made 13 tests fail, including the integration test, where the production VM was recommended. After reverting, all 47 tests passed with no leftover rows.
- **Week 9 checkpoint met:** core backend tests pass and the primary flow is verified by an automated test.
- Carried forward: stale VM handling in sync, alerts that never auto-resolve, recommendations that stay pending after a live stop, and the active-side idle check and real stop, which need a live VM. 