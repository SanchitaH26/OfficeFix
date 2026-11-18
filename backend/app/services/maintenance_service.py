import logging
from typing import Any

from sqlalchemy import and_, func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from ..models import MaintenanceRequest, Technician, utc_now
from ..schemas import DashboardStats, RequestCreate, RequestUpdate, TechnicianCreate, TechnicianUpdate

logger = logging.getLogger(__name__)

NON_NULLABLE_REQUEST_FIELDS = (
    "employee_name",
    "employee_email",
    "title",
    "description",
    "category",
    "location",
    "priority",
    "status",
)
NON_NULLABLE_TECHNICIAN_FIELDS = ("name", "email", "specialization", "availability")


class ServiceError(Exception):
    status_code = 400

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NotFoundError(ServiceError):
    status_code = 404


class ConflictError(ServiceError):
    status_code = 409


class ValidationFailedError(ServiceError):
    status_code = 422


def _commit(db: Session, conflict_message: str | None = None) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        logger.warning("Integrity error: %s", exc.orig)
        raise ConflictError(conflict_message or "The record conflicts with existing data.") from exc
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Database error")
        raise ServiceError("A database error occurred. Please try again.") from exc


def _active_count_subquery():
    return (
        select(MaintenanceRequest.technician_id, func.count(MaintenanceRequest.id).label("active_count"))
        .where(MaintenanceRequest.status != "Resolved", MaintenanceRequest.technician_id.is_not(None))
        .group_by(MaintenanceRequest.technician_id)
        .subquery()
    )


def _with_active_count(db: Session, technicians: list[Technician]) -> list[Technician]:
    if not technicians:
        return technicians
    counts = dict(
        db.execute(
            select(MaintenanceRequest.technician_id, func.count(MaintenanceRequest.id))
            .where(
                MaintenanceRequest.status != "Resolved",
                MaintenanceRequest.technician_id.in_([t.id for t in technicians]),
            )
            .group_by(MaintenanceRequest.technician_id)
        ).all()
    )
    for technician in technicians:
        technician.active_request_count = counts.get(technician.id, 0)
    return technicians


# Requests

def list_requests(
    db: Session,
    status: str | None = None,
    category: str | None = None,
    priority: str | None = None,
) -> list[MaintenanceRequest]:
    stmt = select(MaintenanceRequest).options(joinedload(MaintenanceRequest.technician))
    if status:
        stmt = stmt.where(MaintenanceRequest.status == status)
    if category:
        stmt = stmt.where(MaintenanceRequest.category == category)
    if priority:
        stmt = stmt.where(MaintenanceRequest.priority == priority)
    stmt = stmt.order_by(MaintenanceRequest.created_at.desc(), MaintenanceRequest.id.desc())
    return list(db.execute(stmt).unique().scalars().all())


def get_request(db: Session, request_id: int) -> MaintenanceRequest:
    stmt = (
        select(MaintenanceRequest)
        .options(joinedload(MaintenanceRequest.technician))
        .where(MaintenanceRequest.id == request_id)
        .execution_options(populate_existing=True)
    )
    request = db.execute(stmt).unique().scalar_one_or_none()
    if request is None:
        raise NotFoundError(f"Maintenance request {request_id} was not found.")
    return request


def create_request(db: Session, payload: RequestCreate) -> MaintenanceRequest:
    now = utc_now()
    request = MaintenanceRequest(
        **payload.model_dump(),
        status="Open",
        created_at=now,
        updated_at=now,
    )
    db.add(request)
    _commit(db)
    db.refresh(request)
    return get_request(db, request.id)


def _assert_assignable(db: Session, technician_id: int) -> None:
    technician = db.get(Technician, technician_id)
    if technician is None:
        raise NotFoundError(f"Technician {technician_id} was not found.")
    if technician.availability != "Available":
        raise ValidationFailedError(
            f"Technician {technician.name} is unavailable and cannot be assigned new requests."
        )


def update_request(db: Session, request_id: int, payload: RequestUpdate) -> MaintenanceRequest:
    request = get_request(db, request_id)
    changes: dict[str, Any] = payload.model_dump(exclude_unset=True)

    for field in NON_NULLABLE_REQUEST_FIELDS:
        if field in changes and changes[field] is None:
            raise ValidationFailedError(f"{field} cannot be empty.")

    effective_category = changes.get("category", request.category)
    if effective_category == "Other":
        text = changes["category_other"] if "category_other" in changes else request.category_other
        if not text or not text.strip():
            raise ValidationFailedError("Please specify the category when 'Other' is selected.")
        changes["category_other"] = text.strip()
    else:
        changes["category_other"] = None

    new_technician_id = changes.get("technician_id", request.technician_id)
    if "technician_id" in changes and new_technician_id is not None and new_technician_id != request.technician_id:
        _assert_assignable(db, new_technician_id)

    if "status" in changes:
        if changes["status"] == "Resolved":
            if request.resolved_at is None:
                request.resolved_at = utc_now()
        else:
            request.resolved_at = None

    for field, value in changes.items():
        setattr(request, field, value)

    request.updated_at = utc_now()
    _commit(db, conflict_message="The request could not be saved due to conflicting data.")
    return get_request(db, request_id)


def delete_request(db: Session, request_id: int) -> None:
    request = get_request(db, request_id)
    db.delete(request)
    _commit(db)


# Technicians

def list_technicians(db: Session) -> list[Technician]:
    technicians = list(db.execute(select(Technician).order_by(Technician.name, Technician.id)).scalars().all())
    return _with_active_count(db, technicians)


def get_technician(db: Session, technician_id: int) -> Technician:
    technician = db.get(Technician, technician_id)
    if technician is None:
        raise NotFoundError(f"Technician {technician_id} was not found.")
    return _with_active_count(db, [technician])[0]


def create_technician(db: Session, payload: TechnicianCreate) -> Technician:
    data = payload.model_dump()
    data["email"] = data["email"].lower()
    technician = Technician(**data, created_at=utc_now())
    db.add(technician)
    _commit(db, conflict_message="A technician with this email already exists.")
    db.refresh(technician)
    return get_technician(db, technician.id)


def update_technician(db: Session, technician_id: int, payload: TechnicianUpdate) -> Technician:
    technician = db.get(Technician, technician_id)
    if technician is None:
        raise NotFoundError(f"Technician {technician_id} was not found.")

    changes = payload.model_dump(exclude_unset=True)
    for field in NON_NULLABLE_TECHNICIAN_FIELDS:
        if field in changes and changes[field] is None:
            raise ValidationFailedError(f"{field} cannot be empty.")
    if "email" in changes:
        changes["email"] = changes["email"].lower()

    for field, value in changes.items():
        setattr(technician, field, value)

    _commit(db, conflict_message="A technician with this email already exists.")
    return get_technician(db, technician_id)


# Dashboard

def dashboard_stats(db: Session) -> DashboardStats:
    counts = db.execute(
        select(
            func.count(MaintenanceRequest.id),
            func.count(MaintenanceRequest.id).filter(MaintenanceRequest.status == "Open"),
            func.count(MaintenanceRequest.id).filter(MaintenanceRequest.status == "In Progress"),
            func.count(MaintenanceRequest.id).filter(MaintenanceRequest.status == "Resolved"),
            func.count(MaintenanceRequest.id).filter(
                and_(MaintenanceRequest.priority == "High", MaintenanceRequest.status != "Resolved")
            ),
        )
    ).one()

    technician_counts = db.execute(
        select(
            func.count(Technician.id),
            func.count(Technician.id).filter(Technician.availability == "Available"),
        )
    ).one()

    recent = list(
        db.execute(
            select(MaintenanceRequest)
            .options(joinedload(MaintenanceRequest.technician))
            .order_by(MaintenanceRequest.created_at.desc(), MaintenanceRequest.id.desc())
            .limit(5)
        )
        .unique()
        .scalars()
        .all()
    )

    active_counts = _active_count_subquery()
    workload_rows = db.execute(
        select(
            Technician.id,
            Technician.name,
            Technician.availability,
            func.coalesce(active_counts.c.active_count, 0),
        )
        .outerjoin(active_counts, active_counts.c.technician_id == Technician.id)
        .order_by(Technician.name, Technician.id)
    ).all()

    return DashboardStats(
        total_requests=counts[0],
        open_requests=counts[1],
        in_progress_requests=counts[2],
        resolved_requests=counts[3],
        high_priority_unresolved=counts[4],
        total_technicians=technician_counts[0],
        available_technicians=technician_counts[1],
        recent_requests=recent,
        technician_workload=[
            {"technician_id": row[0], "name": row[1], "availability": row[2], "active_requests": row[3]}
            for row in workload_rows
        ],
    )
