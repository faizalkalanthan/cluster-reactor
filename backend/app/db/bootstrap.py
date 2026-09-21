from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app import models  # noqa: F401
from app.services.auth_seed import seed_demo_tenant_users


def initialize_database() -> None:
    if settings.db_auto_create_tables:
        Base.metadata.create_all(bind=engine)
        with engine.begin() as connection:
            pass

    # Lightweight bootstrap for the local/dev experience.
    try:
        from sqlalchemy.orm import Session

        with Session(bind=engine) as session:
            seed_demo_tenant_users(session)
    except Exception:
        pass