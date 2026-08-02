# 🛡️ Smart Cloud Budget Guard

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Azure](https://img.shields.io/badge/Microsoft_Azure-0089D6?style=for-the-badge&logo=microsoft-azure&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Status](https://img.shields.io/badge/Status-In_Development-yellow?style=for-the-badge)

> A preventive assistant that helps students, academic labs, and small dev teams stop wasting money on forgotten Azure VMs.

## 📖 Project Description

Users frequently spin up cloud VMs for testing and forget to shut them down. **Smart Budget Guard** doesn't just report cost after the fact — it watches VM activity and budget thresholds together, flags idle non-critical resources, and can safely recommend or execute a shutdown.

---

## 🎯 Objectives

- 🔍 **Monitor & Track** — inventory Azure VMs and persist their state.
- 💤 **Detect Idle Resources** — flag low-CPU/low-network VMs using Azure Monitor metrics.
- 💰 **Budget Management** — let users define monthly budgets and warning thresholds.
- 🚨 **Proactive Alerts** — raise alerts when idle resources or spend cross limits.
- 🤖 **Safe Automation** — stop tagged, non-production dev VMs, with dry-run support and full logging.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend framework** | FastAPI (Python 3.11+) |
| **Azure SDK** | `azure-identity`, `azure-mgmt-compute`, `azure-mgmt-monitor` |
| **Authentication** | `DefaultAzureCredential` via Azure CLI login |
| **Database** | PostgreSQL, accessed via SQLAlchemy (sync) + psycopg-binary |
| **Schema management** | Plain SQL in `docs/db_schema.sql`, applied manually |
| **Scheduler** | APScheduler (in-process `BackgroundScheduler`) |
| **Frontend** | React + Vite, Recharts for charts |

---

## ☁️ Azure Services Used

- 🖥️ **Azure Virtual Machines** — inventory + power state
- 📊 **Azure Monitor** — CPU / network metrics for idle detection
- 💵 Cost data — mocked in-app (VM size × stopped hours × hourly rate)

---

## 💻 Development Tools

- **IDE:** VS Code
- **Version Control:** Git & GitHub
- **API Testing:** Postman

---
*Built to keep the cloud affordable! ☁️💸*