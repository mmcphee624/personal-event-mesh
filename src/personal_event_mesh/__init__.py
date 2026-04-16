"""Personal Event Mesh - Machine-enforced event contracts for personal services."""

__version__ = "0.3.0"

from personal_event_mesh.registry import CapabilityReport, register_capability
from personal_event_mesh.validate import validate, validate_or_raise

__all__ = [
    "validate",
    "validate_or_raise",
    "register_capability",
    "CapabilityReport",
]
