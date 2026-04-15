"""Tests for capability registration."""

from personal_event_mesh.registry import CapabilityReport, register_capability


class TestRegisterCapability:
    def test_basic_registration(self):
        report = register_capability(
            name="my-producer",
            version="0.1.0",
            schemas={
                "publishes": ["deal-alert@1.0.0"],
                "consumes": [],
            },
        )
        assert isinstance(report, CapabilityReport)
        assert report.service == "my-producer"
        assert report.version == "0.1.0"
        assert report.mesh_version == "0.1.0"  # from __version__
        assert report.publishes == ["deal-alert@1.0.0"]
        assert report.consumes == []
        assert report.status == "healthy"

    def test_custom_mesh_version(self):
        report = register_capability(
            name="my-consumer",
            version="0.2.0",
            schemas={"consumes": ["monitoring-event@1.0.0"]},
            mesh_version="0.1.0",
        )
        assert report.mesh_version == "0.1.0"

    def test_to_dict(self):
        report = register_capability(
            name="my-consumer",
            version="0.1.0",
            schemas={
                "publishes": [],
                "consumes": ["ha-automation@1.0.0", "monitoring-event@1.0.0"],
            },
        )
        d = report.to_dict()
        assert d["service"] == "my-consumer"
        assert d["contracts"]["consumes"] == [
            "ha-automation@1.0.0",
            "monitoring-event@1.0.0",
        ]
        assert "publishes" in d["contracts"]
        assert d["status"] == "healthy"

    def test_to_dict_validates_against_schema(self):
        from personal_event_mesh.validate import validate

        report = register_capability(
            name="my-consumer",
            version="0.1.0",
            schemas={
                "publishes": [],
                "consumes": ["monitoring-event@1.0.0"],
            },
        )
        errors = validate(report.to_dict(), "capability-report")
        assert errors == []
