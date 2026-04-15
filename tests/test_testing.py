"""Tests for the testing utilities themselves."""

import pytest

from personal_event_mesh.testing import MockStream, assert_contract_compatible, load_fixture


class TestLoadFixture:
    def test_load_existing_fixture(self):
        event = load_fixture("ha-automation/hacs-update.json")
        assert event["event_type"] == "ha_automation"
        assert event["automation_id"] == "hacs_update_notify"

    def test_load_nonexistent_fixture(self):
        with pytest.raises(FileNotFoundError):
            load_fixture("nonexistent/file.json")


class TestAssertContractCompatible:
    def test_valid_event_passes(self):
        event = load_fixture("monitoring-event/uptime-kuma-down.json")
        assert_contract_compatible(event, "monitoring-event")

    def test_invalid_event_raises_assertion(self):
        with pytest.raises(AssertionError, match="Contract violation"):
            assert_contract_compatible({}, "text-event")


class TestMockStream:
    def test_publish_and_get(self):
        stream = MockStream()
        stream.publish("mesh:events", {"type": "test"})
        stream.publish("mesh:deals", {"type": "deal"})

        all_events = stream.get_events()
        assert len(all_events) == 2

        deal_events = stream.get_events("mesh:deals")
        assert len(deal_events) == 1
        assert deal_events[0]["type"] == "deal"

    def test_clear(self):
        stream = MockStream()
        stream.publish("mesh:events", {"type": "test"})
        stream.clear()
        assert stream.get_events() == []
