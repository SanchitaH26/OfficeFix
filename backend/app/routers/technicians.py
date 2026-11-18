from fastapi import APIRouter, status

from ..dependencies import DbSession
from ..schemas import TechnicianCreate, TechnicianResponse, TechnicianUpdate
from ..services import maintenance_service as service

router = APIRouter(prefix="/api/v1/technicians", tags=["technicians"])


@router.get("", response_model=list[TechnicianResponse])
def list_technicians(db: DbSession):
    return service.list_technicians(db)


@router.post("", response_model=TechnicianResponse, status_code=status.HTTP_201_CREATED)
def create_technician(payload: TechnicianCreate, db: DbSession):
    return service.create_technician(db, payload)


@router.get("/{technician_id}", response_model=TechnicianResponse)
def get_technician(technician_id: int, db: DbSession):
    return service.get_technician(db, technician_id)


@router.patch("/{technician_id}", response_model=TechnicianResponse)
def update_technician(technician_id: int, payload: TechnicianUpdate, db: DbSession):
    return service.update_technician(db, technician_id, payload)
