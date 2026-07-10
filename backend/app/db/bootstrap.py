from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app import models  # noqa: F401


def initialize_database() -> None:
    if settings.db_auto_create_tables:
        Base.metadata.create_all(bind=engine)