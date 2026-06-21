from datetime import date

from app.models.contract import Contract

RISK_CRITICAL = "critical"
RISK_WARNING = "warning"
RISK_ATTENTION = "attention"

RISK_THRESHOLDS = {
    RISK_CRITICAL: 7,
    RISK_WARNING: 15,
    RISK_ATTENTION: 30,
}

RISK_LABELS = {
    RISK_CRITICAL: "7天内到期",
    RISK_WARNING: "15天内到期",
    RISK_ATTENTION: "30天内到期",
}

RISK_ORDER = [RISK_CRITICAL, RISK_WARNING, RISK_ATTENTION]


def days_until_expiry(contract: Contract, today: date | None = None) -> int:
    ref = today or date.today()
    return (contract.end_date - ref).days


def get_expiry_risk(contract: Contract, today: date | None = None) -> str | None:
    if contract.status != "active":
        return None
    ref = today or date.today()
    days = (contract.end_date - ref).days
    if days < 0:
        return None
    if days <= RISK_THRESHOLDS[RISK_CRITICAL]:
        return RISK_CRITICAL
    if days <= RISK_THRESHOLDS[RISK_WARNING]:
        return RISK_WARNING
    if days <= RISK_THRESHOLDS[RISK_ATTENTION]:
        return RISK_ATTENTION
    return None


def group_contracts_by_risk(contracts: list[Contract], today: date | None = None) -> dict[str, list[Contract]]:
    ref = today or date.today()
    groups: dict[str, list[Contract]] = {key: [] for key in RISK_ORDER}
    for contract in contracts:
        risk = get_expiry_risk(contract, ref)
        if risk:
            groups[risk].append(contract)
    return groups


def count_by_risk(contracts: list[Contract], today: date | None = None) -> dict[str, int]:
    ref = today or date.today()
    counts: dict[str, int] = {key: 0 for key in RISK_ORDER}
    for contract in contracts:
        risk = get_expiry_risk(contract, ref)
        if risk:
            counts[risk] += 1
    return counts
