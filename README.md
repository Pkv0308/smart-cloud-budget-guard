# Smart cloud budget guard
## Project Description
Smart Budget Guard is a cloud-based system designed to help students, academic labs, and small development teams avoid unnecessary cloud spending by monitoring resource usage, detecting idle virtual machines, and applying budget-aware alerts or safe automation rules.
The project focuses on a practical cloud problem: users often create test or development resources and forget to shut them down, which leads to avoidable costs. Cloud cost-optimization guidance and provider examples consistently recommend idle-resource detection, budget alerts, and automated shutdown workflows as effective ways to control such waste.
Unlike standard financial summary dashboards, Smart Budget Guard is intended to act as a preventive assistant. It combines budget thresholds with resource behavior, such as low CPU activity and resource tags, to identify non-critical resources that can be safely recommended for shutdown or automatically stopped.
## Objectives
•	Build a cloud-connected system that monitors compute resources and spending behavior.
•	Detect idle virtual machines or similar compute resources using utilization metrics such as CPU activity.
•	Allow users to define monthly budgets and warning thresholds.
•	Generate alerts when usage patterns or spending approach configured limits.
•	Provide safe automated control, such as stopping tagged development VMs during off-hours or after long inactivity periods.


## Tools and Technologies
### Cloud Platform
Azure is a strong choice for implementation because Azure documents auto-shutdown scheduling, alert-driven VM automation, and cost alert workflows in a direct and student-friendly way.
### Backend
•	Python with Flask or FastAPI for API development and dashboard integration.
•	Cloud SDKs such as Azure SDK for Python or Boto3 for AWS resource access.
•	Scheduler or background worker for periodic checks.
### Frontend
•	Streamlit for a fast prototype dashboard, or
•	React plus a Python backend for a cleaner full-stack implementation.
### Database
•	SQLite for local development and testing.
•	PostgreSQL if a more robust deployed version is needed.
### Cloud Services
Likely services include:
•	Azure Virtual Machines.
•	Azure Monitor and metric alerts.
•	Azure Automation or Logic Apps for controlled actions.
•	Azure Cost Management for budget and spending reference.
### Development Tools
•	VS Code for development.
•	Git and GitHub for version control.
•	Postman or Thunder Client for API testing.
