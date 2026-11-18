import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from .database import get_engine, get_settings
from .routers import dashboard, requests, technicians
from .services.maintenance_service import ServiceError

logger = logging.getLogger(__name__)

app = FastAPI(title="OfficeFix API", version="1.0.0", redirect_slashes=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Accept"],
)

app.include_router(requests.router)
app.include_router(technicians.router)
app.include_router(dashboard.router)


@app.exception_handler(ServiceError)
async def service_error_handler(_: Request, exc: ServiceError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.exception_handler(SQLAlchemyError)
async def database_error_handler(_: Request, exc: SQLAlchemyError) -> JSONResponse:
    logger.exception("Unhandled database error", exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "A database error occurred."})


@app.get("/health", tags=["health"])
def health():
    try:
        with get_engine().connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        logger.exception("Health check database probe failed")
        return JSONResponse(status_code=503, content={"status": "error", "database": "unreachable"})
    return {"status": "ok", "database": "ok"}
