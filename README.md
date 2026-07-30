# 🛡️ Smart Cloud Budget Guard

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Azure](https://img.shields.io/badge/Microsoft_Azure-0089D6?style=for-the-badge&logo=microsoft-azure&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

> A smart, cloud-based preventive assistant designed to help students, academic labs, and small development teams eliminate unnecessary cloud waste.

## 📖 Project Description

**Smart Budget Guard** tackles a practical and expensive cloud problem: forgotten test or development resources. Users frequently spin up VMs and forget to shut them down, leading to avoidable costs. 

Unlike standard financial summary dashboards that just report costs after the fact, Smart Budget Guard acts as a **preventive assistant**. By combining budget thresholds with resource behavior (like low CPU activity and specific resource tags), it identifies non-critical resources and either safely recommends them for shutdown or automatically stops them.

---

## 🎯 Objectives

- 🔍 **Monitor & Track:** Build a cloud-connected system to monitor compute resources and spending behavior.
- 💤 **Detect Idle Resources:** Identify idle virtual machines using utilization metrics (e.g., CPU activity).
- 💰 **Budget Management:** Enable users to define monthly budgets and warning thresholds.
- 🚨 **Proactive Alerts:** Generate real-time alerts when usage or spending approaches configured limits.
- 🤖 **Safe Automation:** Provide automated controls, such as stopping tagged dev VMs during off-hours or after prolonged inactivity.

---

## 🛠️ Tools and Technologies

### ☁️ Cloud Platform
**Microsoft Azure** is the primary platform of choice. Azure provides excellent documentation for auto-shutdown scheduling, alert-driven VM automation, and cost alert workflows in a direct, student-friendly way.

### 🧰 Tech Stack

| Category | Technologies |
| :--- | :--- |
| **Backend** | 🐍 Python (Flask / FastAPI), Azure SDK, Background Schedulers |
| **Frontend** | 🎨 React  |
| **Database** | 🗄️ PostgreSQL (Robust deployment) |

### ⚙️ Cloud Services
- 🖥️ **Azure Virtual Machines**
- 📊 **Azure Monitor** (Metric alerts)
- ⚡ **Azure Automation / Logic Apps** (Controlled actions)
- 💵 **Azure Cost Management** (Budget & spending reference)

### 💻 Development Tools
- **IDE:** VS Code
- **Version Control:** Git & GitHub
- **API Testing:** Postman 

---
*Built to keep the cloud affordable! ☁️💸*
