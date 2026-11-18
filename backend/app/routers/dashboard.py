from fastapi import APIRouter

from ..dependencies import DbSession
from ..schemas import DashboardStats
from ..services import maintenance_service as service

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def dashboard_stats(db: DbSession):
    return service.dashboard_stats(db)
