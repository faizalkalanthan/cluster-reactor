from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db_session
from app.main import app
from app.models.tenant import Tenant
from app.models.user import User

from tests.backend.api.clients.auth_client import AuthClient
from tests.backend.api.clients.health_client import HealthClient
from tests.backend.api.clients.incident_client import IncidentClient
from tests.backend.api.clients.tenant_client import TenantClient
from tests.backend.api.config.config import ApiTestConfig
from tests.backend.api.schemas.incident_schema import build_incident_payload
from tests.backend.api.schemas.tenant_schema import build_tenant_payload
from tests.backend.api.schemas.tenant_schema import build_tenant_update_payload
from tests.backend.api.utils.json_loader import load_json_file


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(bind=engine)
TEST_DATA_PATH = Path(__file__).resolve().parent / "test_data"


def override_get_db_session() -> Generator[Session, None, None]:
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(autouse=True)
def reset_api_database() -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    seed_session = TestingSessionLocal()
    tenant = Tenant(name="Cluster Reactor", slug=ApiTestConfig.TENANT_SLUG, domain="clusterreactor.local", is_active=True)
    seed_session.add(tenant)
    seed_session.flush()
    seed_session.add(
        User(
            email=ApiTestConfig.ADMIN_EMAIL,
            full_name="Cluster Reactor Admin",
            password_hash=hash_password(ApiTestConfig.ADMIN_PASSWORD),
            role="admin",
            is_active=True,
            tenant_id=tenant.id,
        )
    )
    seed_session.commit()
    seed_session.close()
    app.dependency_overrides[get_db_session] = override_get_db_session
    yield
    app.dependency_overrides.pop(get_db_session, None)


@pytest.fixture()
def api_session() -> Generator[Session, None, None]:
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def auth_data() -> dict:
    return load_json_file(TEST_DATA_PATH / "auth.json")


@pytest.fixture()
def incident_data() -> dict:
    return load_json_file(TEST_DATA_PATH / "incidents.json")


@pytest.fixture()
def tenant_data() -> dict:
    return load_json_file(TEST_DATA_PATH / "tenants.json")


@pytest.fixture()
def auth_client(client: TestClient) -> AuthClient:
    return AuthClient(client)


@pytest.fixture()
def health_client(client: TestClient) -> HealthClient:
    return HealthClient(client)


@pytest.fixture()
def incident_client(client: TestClient) -> IncidentClient:
    return IncidentClient(client)


@pytest.fixture()
def admin_token(auth_client: AuthClient, auth_data: dict) -> str:
    login_data = auth_data["admin_login"]
    response = auth_client.login(
        email=login_data["email"],
        password=login_data["password"],
        tenant_slug=login_data["tenant_slug"],
    )
    return response.json()["access_token"]


@pytest.fixture()
def tenant_client(client: TestClient, admin_token: str) -> TenantClient:
    return TenantClient(client, token=admin_token)


@pytest.fixture()
def valid_incident_data(incident_data: dict) -> dict:
    payload = incident_data["valid_incident"]
    return build_incident_payload(**payload)


@pytest.fixture()
def valid_tenant_data(tenant_data: dict) -> dict:
    payload = tenant_data["valid_tenant"]
    return build_tenant_payload(**payload)


@pytest.fixture()
def updated_tenant_data(tenant_data: dict) -> dict:
    payload = tenant_data["updated_tenant"]
    return build_tenant_update_payload(**payload)