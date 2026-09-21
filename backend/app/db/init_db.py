from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.tenant import Tenant
from app.models.user import User


def init_db(db: Session) -> None:
    """Initialize database with demo tenant and users."""
    
    # Check if default tenant exists
    default_tenant = db.query(Tenant).filter(Tenant.slug == "clusterreactor").first()
    if not default_tenant:
        default_tenant = Tenant(
            name="Cluster Reactor",
            slug="clusterreactor",
            domain="clusterreactor.local",
            is_active=True,
        )
        db.add(default_tenant)
        db.commit()
        db.refresh(default_tenant)
    
    # Seed demo users if they don't exist
    demo_users = [
        {
            "email": "admin@clusterreactor.local",
            "full_name": "Admin User",
            "password": "Admin123!",
            "role": "admin",
        },
        {
            "email": "writer@clusterreactor.local",
            "full_name": "Writer User",
            "password": "Writer123!",
            "role": "writer",
        },
        {
            "email": "reader@clusterreactor.local",
            "full_name": "Reader User",
            "password": "Reader123!",
            "role": "reader",
        },
    ]
    
    for user_data in demo_users:
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing_user:
            user = User(
                email=user_data["email"],
                full_name=user_data["full_name"],
                password_hash=hash_password(user_data["password"]),
                role=user_data["role"],
                is_active=True,
                tenant_id=default_tenant.id,
            )
            db.add(user)
    
    db.commit()
