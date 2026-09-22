class ApiTestConfig:
    HEALTH_ENDPOINT = "/healthz"
    READINESS_ENDPOINT = "/readyz"
    LOGIN_ENDPOINT = "/api/v1/auth/login"
    INCIDENTS_ENDPOINT = "/api/v1/incidents"
    TENANTS_ENDPOINT = "/api/v1/tenants"

    ADMIN_EMAIL = "admin@clusterreactor.local"
    ADMIN_PASSWORD = "Admin123!"
    TENANT_SLUG = "clusterreactor"