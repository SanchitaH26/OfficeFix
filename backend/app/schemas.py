from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
# Names: letters, spaces, hyphen, apostrophe, period. No digits, symbols, or emoji.
NAME_PATTERN = r"^[\p{L} .'\-]+$"
# Titles and locations: letters, digits, spaces, and . , - ( ) / & ' #
TEXT_PATTERN = r"^[\p{L}\p{N} .,\-()/&'#]+$"

Category = Literal["Electrical", "HVAC/AC", "Plumbing", "Internet/Network", "Furniture", "Other"]
Priority = Literal["Low", "Medium", "High"]
Status = Literal["Open", "In Progress", "Resolved"]
Availability = Literal["Available", "Unavailable"]


class _Base(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class RequestCreate(_Base):
    employee_name: str = Field(min_length=1, max_length=120, pattern=NAME_PATTERN)
    employee_email: str = Field(min_length=3, max_length=254, pattern=EMAIL_PATTERN)
    title: str = Field(min_length=1, max_length=200, pattern=TEXT_PATTERN)
    description: str = Field(min_length=1, max_length=5000)
    category: Category
    category_other: str | None = Field(default=None, min_length=1, max_length=100, pattern=TEXT_PATTERN)
    location: str = Field(min_length=1, max_length=200, pattern=TEXT_PATTERN)
    priority: Priority

    @model_validator(mode="after")
    def require_other_category_text(self):
        if self.category == "Other":
            if not self.category_other:
                raise ValueError("Please specify the category when 'Other' is selected.")
        else:
            self.category_other = None
        return self


class RequestUpdate(_Base):
    employee_name: str | None = Field(default=None, min_length=1, max_length=120, pattern=NAME_PATTERN)
    employee_email: str | None = Field(default=None, min_length=3, max_length=254, pattern=EMAIL_PATTERN)
    title: str | None = Field(default=None, min_length=1, max_length=200, pattern=TEXT_PATTERN)
    description: str | None = Field(default=None, min_length=1, max_length=5000)
    category: Category | None = None
    category_other: str | None = Field(default=None, min_length=1, max_length=100, pattern=TEXT_PATTERN)
    location: str | None = Field(default=None, min_length=1, max_length=200, pattern=TEXT_PATTERN)
    priority: Priority | None = None
    status: Status | None = None
    technician_id: int | None = Field(default=None, gt=0)
    resolution_notes: str | None = Field(default=None, max_length=5000)


class RequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_name: str
    employee_email: str
    title: str
    description: str
    category: str
    category_other: str | None
    location: str
    priority: str
    status: str
    technician_id: int | None
    technician_name: str | None
    resolution_notes: str | None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None


class TechnicianCreate(_Base):
    name: str = Field(min_length=1, max_length=120, pattern=NAME_PATTERN)
    email: str = Field(min_length=3, max_length=254, pattern=EMAIL_PATTERN)
    specialization: str = Field(min_length=1, max_length=120, pattern=TEXT_PATTERN)
    availability: Availability = "Available"


class TechnicianUpdate(_Base):
    name: str | None = Field(default=None, min_length=1, max_length=120, pattern=NAME_PATTERN)
    email: str | None = Field(default=None, min_length=3, max_length=254, pattern=EMAIL_PATTERN)
    specialization: str | None = Field(default=None, min_length=1, max_length=120, pattern=TEXT_PATTERN)
    availability: Availability | None = None


class TechnicianResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    specialization: str
    availability: str
    created_at: datetime
    active_request_count: int


class TechnicianWorkload(BaseModel):
    technician_id: int
    name: str
    availability: str
    active_requests: int


class DashboardStats(BaseModel):
    total_requests: int
    open_requests: int
    in_progress_requests: int
    resolved_requests: int
    high_priority_unresolved: int
    total_technicians: int
    available_technicians: int
    recent_requests: list[RequestResponse]
    technician_workload: list[TechnicianWorkload]
