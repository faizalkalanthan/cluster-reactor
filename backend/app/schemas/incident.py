from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class IncidentSeverity(StrEnum):
    SEV_1 = "sev-1"
    SEV_2 = "sev-2"
    SEV_3 = "sev-3"
    SEV_4 = "sev-4"


class IncidentStatus(StrEnum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class IncidentCreate(BaseModel): #Data coming into your application when someone creates an incident.
    title: str = Field(min_length=3, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    severity: IncidentSeverity = IncidentSeverity.SEV_3
    status: IncidentStatus = IncidentStatus.OPEN
    affected_service: str = Field(default="backend", min_length=2, max_length=128)


class IncidentRead(BaseModel): #Data going out of your application when you return an incident to the client.
    id: int
    title: str
    description: str | None
    severity: IncidentSeverity
    status: IncidentStatus
    affected_service: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
