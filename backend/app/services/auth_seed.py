from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.tenant import Tenant
from app.models.user import User


def seed_demo_tenant_users(db_session: Session) -> None:
    tenant = db_session.query(Tenant).filter(Tenant.slug == "clusterreactor").first()
    if tenant is None:
        tenant = Tenant(name="Cluster Reactor", slug="clusterreactor", domain="clusterreactor.local", is_active=True)
        db_session.add(tenant)
        db_session.flush()

    demo_users = [
        {
            "email": "admin@clusterreactor.local",
            "full_name": "Cluster Reactor Admin",
            "password": "Admin123!",
            "role": "admin",
        },
        {
            "email": "writer@clusterreactor.local",
            "full_name": "Cluster Reactor Writer",
            "password": "Writer123!",
            "role": "writer",
        },
        {
            "email": "reader@clusterreactor.local",
            "full_name": "Cluster Reactor Reader",
            "password": "Reader123!",
            "role": "reader",
        },
    ]

    for payload in demo_users:
        email = payload["email"].lower()
        existing = db_session.query(User).filter(User.email == email).first()
        if existing is not None:
            continue
        db_session.add(
            User(
                email=email,
                full_name=payload["full_name"],
                password_hash=hash_password(payload["password"]),
                role=payload["role"],
                tenant_id=tenant.id,
                is_active=True,
            )
        )

    db_session.commit()
