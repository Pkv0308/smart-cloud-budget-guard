from fastapi import FastAPI

from app.vms import router as vms_router

app=FastAPI(
    title="Smart Budget Guard",
    description="Azure Cloud Cost Optimization - Preventive budget guard for dev VMs",
    version="0.1.0"
)

@app.get("/")

def root() -> dict[str,str]:
    return {"service":"Smart Budget Guard","status":"running"}

@app.get("/health")
def health()->dict[str,str]:
    return {"status":"ok"}

app.include_router(vms_router)