from fastapi import FastAPI
from backend.app.vms import router as vms_router
from backend.app.services.scheduler import start_scheduler, scheduler
from contextlib import asynccontextmanager
from backend.app.budgets import router as budgets_router
from backend.app.alerts import router as alerts_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting scheduler...")
    start_scheduler()
    print("Scheduler Jobs: ",scheduler.get_jobs())
    yield


app=FastAPI(
    title="Smart Budget Guard",
    description="Azure Cloud Cost Optimization - Preventive budget guard for dev VMs",
    version="0.1.0",
    lifespan=lifespan,
)

@app.get("/")
def root() -> dict[str,str]:
    return {"service":"Smart Budget Guard","status":"running"}

@app.get("/health")
def health()->dict[str,str]:
    return {"status":"ok"}

app.include_router(vms_router)
app.include_router(budgets_router)
app.include_router(alerts_router)