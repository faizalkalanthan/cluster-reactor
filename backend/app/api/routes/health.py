from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@router.get("/readyz")
def readyz() -> dict:
    # Phase 1.5 will include real DB readiness checks.
    return {"status": "ready", "checks": {"database": "pending"}}