"""Capability registration and discovery."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CapabilityReport:
    """A service's capability report for the /capabilities endpoint."""

    service: str
    version: str
    mesh_version: str
    publishes: list[str] = field(default_factory=list)
    consumes: list[str] = field(default_factory=list)
    status: str = "healthy"

    def to_dict(self) -> dict:
        return {
            "service": self.service,
            "version": self.version,
            "mesh_version": self.mesh_version,
            "contracts": {
                "publishes": self.publishes,
                "consumes": self.consumes,
            },
            "status": self.status,
        }


def register_capability(
    name: str,
    version: str,
    schemas: dict[str, list[str]],
    mesh_version: str | None = None,
) -> CapabilityReport:
    """Build a CapabilityReport for this service.

    Args:
        name: Service name (e.g., "my-api", "my-worker")
        version: Service version (e.g., "0.1.0")
        schemas: Dict with "publishes" and/or "consumes" lists
                 (e.g., {"publishes": ["monitoring-event@1.0.0"], "consumes": []})
        mesh_version: Override mesh version. Defaults to installed package version.
    """
    from personal_event_mesh import __version__

    return CapabilityReport(
        service=name,
        version=version,
        mesh_version=mesh_version or __version__,
        publishes=schemas.get("publishes", []),
        consumes=schemas.get("consumes", []),
    )


async def get_capabilities(service_url: str, timeout: float = 5.0) -> dict | None:
    """Query a service's /capabilities endpoint.

    Returns the parsed JSON response, or None on any failure.
    Requires the 'http' extra: pip install personal-event-mesh[http]
    """
    try:
        import httpx
    except ImportError:
        raise ImportError(
            "httpx is required for get_capabilities(). "
            "Install with: pip install personal-event-mesh[http]"
        )

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{service_url.rstrip('/')}/capabilities", timeout=timeout)
            resp.raise_for_status()
            return resp.json()
    except Exception:
        return None
