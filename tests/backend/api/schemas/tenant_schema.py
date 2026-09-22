from __future__ import annotations


def build_tenant_payload(
    name: str = "Cluster Reactor West",
    slug: str = "cluster-reactor-west",
    domain: str = "west.clusterreactor.local",
    is_active: bool = True,
) -> dict:
    return {
        "name": name,
        "slug": slug,
        "domain": domain,
        "is_active": is_active,
    }


def build_tenant_update_payload(
    name: str = "Cluster Reactor West Updated",
    domain: str = "updated.clusterreactor.local",
    is_active: bool = True,
) -> dict:
    return {
        "name": name,
        "domain": domain,
        "is_active": is_active,
    }