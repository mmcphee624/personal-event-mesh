"""Backwards-compatibility checking for schema changes."""

from __future__ import annotations


def check_backwards_compatible(old_schema: dict, new_schema: dict) -> list[str]:
    """Check that new_schema is backwards-compatible with old_schema.

    Rules enforced:
    - Cannot remove required fields
    - Cannot add new required fields (would break existing producers)
    - Cannot remove properties entirely
    - Cannot remove enum values (narrows accepted inputs)

    Returns a list of breaking change descriptions. Empty list means compatible.
    """
    breaking: list[str] = []

    old_required = set(old_schema.get("required", []))
    new_required = set(new_schema.get("required", []))

    # New required fields that weren't required before
    added_required = new_required - old_required
    if added_required:
        breaking.append(f"New required fields added: {sorted(added_required)}")

    # Required fields removed (loosening is OK for consumers, but signals a contract change)
    removed_required = old_required - new_required
    if removed_required:
        breaking.append(f"Required fields removed: {sorted(removed_required)}")

    # Properties removed entirely
    old_props = set(old_schema.get("properties", {}).keys())
    new_props = set(new_schema.get("properties", {}).keys())
    removed_props = old_props - new_props
    if removed_props:
        breaking.append(f"Properties removed: {sorted(removed_props)}")

    # Enum value narrowing
    for prop_name in old_props & new_props:
        old_prop = old_schema["properties"][prop_name]
        new_prop = new_schema["properties"][prop_name]
        if "enum" in old_prop and "enum" in new_prop:
            removed_values = set(old_prop["enum"]) - set(new_prop["enum"])
            if removed_values:
                breaking.append(
                    f"Enum values removed from '{prop_name}': {sorted(removed_values)}"
                )

    return breaking
