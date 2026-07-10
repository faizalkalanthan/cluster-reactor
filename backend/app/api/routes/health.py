from fastapi import APIRouter
from fastapi import status
from fastapi.responses import JSONResponse

from app.db.health import check_database_connection

router = APIRouter(tags=["health"])


@router.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@router.get("/readyz")
def readyz() -> JSONResponse:
    database_available, message = check_database_connection()
    if not database_available:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "checks": {"database": "unavailable"},
                "details": {"database": message},
            },
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "ready",
            "checks": {"database": "available"},
        },
    )