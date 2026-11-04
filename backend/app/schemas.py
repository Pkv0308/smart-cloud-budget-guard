from pydantic import BaseModel


class ResourceOut(BaseModel):
    vm_name: str
    vm_id: str | None = None
    vm_size: str | None = None
    location: str | None = None
    power_state: str | None = None
    environment: str | None = None
    owner: str | None = None
    project: str | None = None
    tags: dict[str, str] | None = None
    last_synced_at: str | None = None


class SyncOut(BaseModel):
    synced: int


class IdleVmsOut(BaseModel):
    idle_vms: list[str]


class BudgetOut(BaseModel):
    id: int
    project: str
    monthly_limit: float
    warning_threshold_percent: float | None = None
    critical_threshold_percent: float | None = None


class SpendOut(BaseModel):
    budget_id: int
    project: str
    monthly_limit: float
    current_spend: float
    state: str


class AlertOut(BaseModel):
    id: int
    alert_type: str
    vm_name: str | None = None
    budget_id: int | None = None
    severity: str
    message: str
    acknowledged: bool
    created_at: str | None = None


class AlertAckOut(BaseModel):
    id: int
    acknowledged: bool


class RecommendationOut(BaseModel):
    id: int
    vm_name: str
    reason: str
    status: str
    created_at: str | None = None


class RecommendResult(BaseModel):
    vm_name: str
    status: str
    recommendation_id: int | None = None


class AutomationLogOut(BaseModel):
    id: int
    vm_name: str
    action: str
    dry_run: bool
    result: str
    detail: str | None = None
    created_at: str | None = None


class RunResult(BaseModel):
    vm_name: str
    result: str
    detail: str