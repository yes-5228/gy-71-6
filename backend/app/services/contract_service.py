from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.contract import Contract
from app.models.workstation import Workstation
from app.schemas.contract import (
    ContractCreate,
    ContractRead,
    ContractUpdate,
    ExpiringContractGroup,
    ExpiringContractGroups,
)
from app.services.expiry_service import (
    RISK_LABELS,
    RISK_ORDER,
    RISK_THRESHOLDS,
    days_until_expiry,
    get_expiry_risk,
    group_contracts_by_risk,
)


def _enrich_contract(contract: Contract, today: date | None = None) -> dict:
    ref = today or date.today()
    data = ContractRead.model_validate(contract).model_dump()
    data["expiry_risk"] = get_expiry_risk(contract, ref)
    data["days_until_expiry"] = days_until_expiry(contract, ref) if contract.status == "active" else None
    return data


def list_contracts(db: Session, status: str | None = None) -> list[dict]:
    stmt = (
        select(Contract)
        .options(joinedload(Contract.workstation))
        .order_by(Contract.end_date.asc())
    )
    if status:
        stmt = stmt.where(Contract.status == status)
    contracts = list(db.scalars(stmt).all())
    today = date.today()
    return [_enrich_contract(c, today) for c in contracts]


def create_contract(db: Session, payload: ContractCreate) -> dict:
    workstation = db.get(Workstation, payload.workstation_id)
    if not workstation:
        raise ValueError("workstation_not_found")
    if workstation.status not in {"available", "reserved"}:
        raise ValueError("workstation_not_available")
    if payload.end_date <= payload.start_date:
        raise ValueError("invalid_contract_dates")

    contract = Contract(
        **payload.model_dump(),
        contract_no=f"CT-{date.today().strftime('%Y%m%d')}-{payload.workstation_id:03d}",
        status="active",
    )
    workstation.status = "leased"
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return _enrich_contract(contract)


def update_contract(db: Session, contract_id: int, payload: ContractUpdate) -> dict | None:
    contract = db.get(Contract, contract_id)
    if not contract:
        return None
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(contract, key, value)
    if contract.status in {"terminated", "expired"} and contract.workstation:
        contract.workstation.status = "available"
    db.commit()
    db.refresh(contract)
    return _enrich_contract(contract)


def expiring_contracts_grouped(db: Session) -> ExpiringContractGroups:
    today = date.today()
    until_30 = date.fromordinal(today.toordinal() + 30)
    stmt = (
        select(Contract)
        .options(joinedload(Contract.workstation))
        .where(Contract.status == "active", Contract.end_date >= today, Contract.end_date <= until_30)
        .order_by(Contract.end_date.asc())
    )
    contracts = list(db.scalars(stmt).all())
    groups = group_contracts_by_risk(contracts, today)

    enriched_groups: dict[str, ExpiringContractGroup] = {}
    total_count = 0
    for risk_level in RISK_ORDER:
        group_contracts = groups[risk_level]
        enriched = [_enrich_contract(c, today) for c in group_contracts]
        count = len(enriched)
        total_count += count
        enriched_groups[risk_level] = ExpiringContractGroup(
            risk_level=risk_level,
            risk_label=RISK_LABELS[risk_level],
            threshold_days=RISK_THRESHOLDS[risk_level],
            contracts=enriched,
            count=count,
        )

    return ExpiringContractGroups(
        critical=enriched_groups["critical"],
        warning=enriched_groups["warning"],
        attention=enriched_groups["attention"],
        total_count=total_count,
    )


def expiring_contracts(db: Session, days: int) -> list[dict]:
    today = date.today()
    until = date.fromordinal(today.toordinal() + days)
    stmt = (
        select(Contract)
        .options(joinedload(Contract.workstation))
        .where(Contract.status == "active", Contract.end_date >= today, Contract.end_date <= until)
        .order_by(Contract.end_date.asc())
    )
    contracts = list(db.scalars(stmt).all())
    return [_enrich_contract(c, today) for c in contracts]
