"""Tests for schema validation."""

import pytest
from jsonschema import ValidationError

from personal_event_mesh.validate import validate, validate_or_raise


class TestValidate:
    def test_valid_ha_automation(self):
        event = {
            "event_type": "ha_automation",
            "automation_id": "hacs_update_notify",
            "event_id": "ctx-abc123",
            "data": {"friendly_name": "HACS Update"},
        }
        assert validate(event, "ha-automation") == []

    def test_invalid_ha_automation_missing_field(self):
        event = {
            "event_type": "ha_automation",
            "automation_id": "hacs_update_notify",
            # missing event_id
            "data": {},
        }
        errors = validate(event, "ha-automation")
        assert len(errors) > 0
        assert any("event_id" in e for e in errors)

    def test_valid_monitoring_event(self):
        event = {
            "event_type": "monitoring_event",
            "source": "uptime_kuma",
            "severity": "critical",
            "title": "Scotty is DOWN",
            "message": "Monitor detected down",
            "data": {"monitor_name": "Scotty", "status": "down"},
        }
        assert validate(event, "monitoring-event") == []

    def test_monitoring_event_invalid_source(self):
        event = {
            "event_type": "monitoring_event",
            "source": "unknown_source",
            "title": "Something happened",
        }
        errors = validate(event, "monitoring-event")
        assert len(errors) > 0

    def test_valid_text_event(self):
        event = {"text": "Deployed services: web-app."}
        assert validate(event, "text-event") == []

    def test_text_event_empty_string(self):
        event = {"text": ""}
        errors = validate(event, "text-event")
        assert len(errors) > 0

    def test_valid_roadmap_event(self):
        event = {
            "event_type": "idea.enriched",
            "idea_id": 42,
            "data": {"title": "New feature"},
        }
        assert validate(event, "roadmap-event") == []

    def test_roadmap_event_invalid_type(self):
        event = {
            "event_type": "unknown.event",
            "idea_id": 1,
        }
        errors = validate(event, "roadmap-event")
        assert len(errors) > 0

    def test_valid_deploy_event(self):
        event = {
            "event_type": "deploy_event",
            "source": "github_actions",
            "repo": "my-infra",
            "status": "success",
        }
        assert validate(event, "deploy-event") == []

    def test_valid_deal_alert(self):
        event = {
            "event_type": "deal_alert",
            "source": "price_tracker",
            "item_name": "Weber Genesis",
            "current_price": 649.99,
        }
        assert validate(event, "deal-alert") == []

    def test_valid_capability_report(self):
        report = {
            "service": "my-consumer",
            "version": "0.1.0",
            "mesh_version": "0.1.0",
            "contracts": {
                "publishes": [],
                "consumes": ["monitoring-event@1.0.0"],
            },
            "status": "healthy",
        }
        assert validate(report, "capability-report") == []

    def test_capability_report_invalid_contract_format(self):
        report = {
            "service": "my-consumer",
            "version": "0.1.0",
            "mesh_version": "0.1.0",
            "contracts": {
                "publishes": ["bad format no version"],
                "consumes": [],
            },
            "status": "healthy",
        }
        errors = validate(report, "capability-report")
        assert len(errors) > 0

    def test_unknown_schema_raises(self):
        with pytest.raises(FileNotFoundError):
            validate({}, "nonexistent-schema")

    def test_additional_properties_rejected(self):
        event = {
            "event_type": "ha_automation",
            "automation_id": "test",
            "event_id": "test",
            "data": {},
            "extra_field": "should fail",
        }
        errors = validate(event, "ha-automation")
        assert len(errors) > 0


class TestValidateOrRaise:
    def test_valid_event_no_exception(self):
        event = {"text": "Hello"}
        validate_or_raise(event, "text-event")

    def test_invalid_event_raises(self):
        with pytest.raises(ValidationError):
            validate_or_raise({}, "text-event")
