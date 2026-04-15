"""Tests for backwards-compatibility checking."""

from personal_event_mesh.compat import check_backwards_compatible


class TestBackwardsCompatibility:
    def test_identical_schemas_compatible(self):
        schema = {
            "type": "object",
            "required": ["name"],
            "properties": {"name": {"type": "string"}},
        }
        assert check_backwards_compatible(schema, schema) == []

    def test_adding_optional_property_is_compatible(self):
        old = {
            "type": "object",
            "required": ["name"],
            "properties": {"name": {"type": "string"}},
        }
        new = {
            "type": "object",
            "required": ["name"],
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
            },
        }
        assert check_backwards_compatible(old, new) == []

    def test_removing_property_is_breaking(self):
        old = {
            "type": "object",
            "required": ["name", "age"],
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
            },
        }
        new = {
            "type": "object",
            "required": ["name"],
            "properties": {"name": {"type": "string"}},
        }
        breaking = check_backwards_compatible(old, new)
        assert len(breaking) > 0
        assert any("age" in b for b in breaking)

    def test_adding_required_field_is_breaking(self):
        old = {
            "type": "object",
            "required": ["name"],
            "properties": {"name": {"type": "string"}},
        }
        new = {
            "type": "object",
            "required": ["name", "email"],
            "properties": {
                "name": {"type": "string"},
                "email": {"type": "string"},
            },
        }
        breaking = check_backwards_compatible(old, new)
        assert len(breaking) > 0
        assert any("email" in b for b in breaking)

    def test_removing_enum_value_is_breaking(self):
        old = {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["info", "warning", "critical"]},
            },
        }
        new = {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["info", "warning"]},
            },
        }
        breaking = check_backwards_compatible(old, new)
        assert len(breaking) > 0
        assert any("critical" in b for b in breaking)

    def test_adding_enum_value_is_compatible(self):
        old = {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["info", "warning"]},
            },
        }
        new = {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["info", "warning", "critical"]},
            },
        }
        assert check_backwards_compatible(old, new) == []

    def test_new_schema_no_properties(self):
        old = {
            "type": "object",
            "required": ["name"],
            "properties": {"name": {"type": "string"}},
        }
        new = {"type": "object"}
        breaking = check_backwards_compatible(old, new)
        assert len(breaking) > 0
