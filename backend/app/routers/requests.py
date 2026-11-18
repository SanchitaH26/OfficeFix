from fastapi import APIRouter, Response, status

from ..dependencies import DbSession
from ..schemas import Category, Priority, RequestCreate, RequestResponse, RequestUpdate, Status
from ..services import maintenance_service as service

router = APIRouter(prefix="/api/v1/requests", tags=["requests"])


@router.get("", response_model=list[RequestResponse])
def list_requests(
    db: DbSession,
    status: Status | None = None,
    category: Category | None = None,
    priority: Priority | None = None,
):
    return service.list_requests(db, status=status, category=category, priority=priority)


@router.post("", response_model=RequestResponse, status_code=status.HTTP_201_CREATED)
def create_request(payload: RequestCreate, db: DbSession):
    return service.create_request(db, payload)


@router.get("/{request_id}", response_model=RequestResponse)
def get_request(request_id: int, db: DbSession):
    return service.get_request(db, request_id)


@router.patch("/{request_id}", response_model=RequestResponse)
def update_request(request_id: int, payload: RequestUpdate, db: DbSession):
    return service.update_request(db, request_id, payload)


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_request(request_id: int, db: DbSession):
    service.delete_request(db, request_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
