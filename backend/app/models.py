from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

CATEGORIES = ("Electrical", "HVAC/AC", "Plumbing", "Internet/Network", "Furniture", "Other")
PRIORITIES = ("Low", "Medium", "High")
STATUSES = ("Open", "In Progress", "Resolved")
AVAILABILITIES = ("Available", "Unavailable")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _sql_in(values: tuple[str, ...]) -> str:
    return ", ".join(f"'{value}'" for value in values)


class Technician(Base):
    __tablename__ = "technicians"
    __table_args__ = (
        CheckConstraint(f"availability IN ({_sql_in(AVAILABILITIES)})", name="ck_technicians_availability"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(254), unique=True)
    specialization: Mapped[str] = mapped_column(String(120))
    availability: Mapped[str] = mapped_column(String(20), default="Available", server_default="Available")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, server_default=func.now()
    )


class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"
    __table_args__ = (
        CheckConstraint(f"category IN ({_sql_in(CATEGORIES)})", name="ck_requests_category"),
        CheckConstraint(
            "category <> 'Other' OR (category_other IS NOT NULL AND length(btrim(category_other)) > 0)",
            name="ck_requests_other_category_text",
        ),
        CheckConstraint(
            "category_other IS NULL OR category = 'Other'",
            name="ck_requests_category_other_only_for_other",
        ),
        CheckConstraint(f"priority IN ({_sql_in(PRIORITIES)})", name="ck_requests_priority"),
        CheckConstraint(f"status IN ({_sql_in(STATUSES)})", name="ck_requests_status"),
        CheckConstraint(
            "status <> 'Resolved' OR resolved_at IS NOT NULL",
            name="ck_requests_resolved_has_date",
        ),
        Index("ix_requests_status_priority", "status", "priority"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_name: Mapped[str] = mapped_column(String(120))
    employee_email: Mapped[str] = mapped_column(String(254))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(40), index=True)
    category_other: Mapped[str | None] = mapped_column(String(100), nullable=True)
    location: Mapped[str] = mapped_column(String(200))
    priority: Mapped[str] = mapped_column(String(10), index=True)
    status: Mapped[str] = mapped_column(String(20), default="Open", server_default="Open")
    technician_id: Mapped[int | None] = mapped_column(
        ForeignKey("technicians.id", ondelete="SET NULL"), nullable=True, index=True
    )
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, server_default=func.now(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, server_default=func.now(), onupdate=utc_now
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    technician: Mapped[Technician | None] = relationship()

    @property
    def technician_name(self) -> str | None:
        return self.technician.name if self.technician else None
