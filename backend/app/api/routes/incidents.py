from fastapi import APIRouter
from fastapi import Depends
from fastapi import status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.models.incident import Incident
from app.schemas.incident import IncidentCreate
from app.schemas.incident import IncidentRead

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.get("", response_model=list[IncidentRead])
def list_incidents(db_session: Session = Depends(get_db_session)) -> list[Incident]:
    statement = select(Incident).order_by(Incident.created_at.desc(), Incident.id.desc())
    return list(db_session.scalars(statement).all())


@router.post("", response_model=IncidentRead, status_code=status.HTTP_201_CREATED)
def create_incident(
    payload: IncidentCreate,
    db_session: Session = Depends(get_db_session),
) -> Incident:
    incident = Incident(**payload.model_dump())
    db_session.add(incident)
    db_session.commit()
    db_session.refresh(incident)
    return incident
