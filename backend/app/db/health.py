from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import SessionLocal


def check_database_connection() -> tuple[bool, str]:
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
        return True, "available"
    except SQLAlchemyError as exc:
        return False, str(exc)