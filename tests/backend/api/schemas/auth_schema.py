from __future__ import annotations


def build_login_payload(email: str, password: str, tenant_slug: str) -> dict:
    return {
        "email": email,
        "password": password,
        "tenant_slug": tenant_slug,
    }