from pydantic import BaseModel


class ExpiryRiskCounts(BaseModel):
    critical: int
    warning: int
    attention: int
    total: int


class DashboardStats(BaseModel):
    total_workstations: int
    available_workstations: int
    leased_workstations: int
    active_contracts: int
    unpaid_amount: float
    overdue_amount: float
    expiring_contracts: int
    expiring_critical: int
    expiring_warning: int
    expiring_attention: int
