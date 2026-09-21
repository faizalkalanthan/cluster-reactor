from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.db.session import get_db_session
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db_session: Session = Depends(get_db_session)) -> TokenResponse:
    user = db_session.query(User).filter(User.email == payload.email.lower()).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if payload.tenant_slug:
        tenant = db_session.query(Tenant).filter(Tenant.slug == payload.tenant_slug).first()
        if tenant is None or tenant.id != user.tenant_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not assigned to this tenant")

    token = create_access_token(user.id, user.tenant_id, user.role)
    return TokenResponse(access_token=token)
