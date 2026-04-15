# personal-event-mesh

Machine-enforced event contracts for personal services.

## What this is

JSON Schema definitions + a Python validation package for the events flowing between your services. Catches contract drift at CI time, not at 3am.

## Install

```bash
# Pin to a tagged release, never HEAD
pip install "personal-event-mesh @ git+https://github.com/mmcphee624/personal-event-mesh@v0.1.0"
```

## Usage

### Validate an event

```python
from personal_event_mesh import validate, validate_or_raise

errors = validate(event, "monitoring-event")  # returns list of error strings
validate_or_raise(event, "monitoring-event")  # raises ValidationError
```

### Register capabilities

```python
from personal_event_mesh import register_capability

report = register_capability(
    name="my-producer",
    version="0.1.0",
    schemas={
        "publishes": ["deal-alert@1.0.0"],
        "consumes": [],
    },
)
# Use report.to_dict() in your GET /capabilities endpoint
```

### Test helpers

```python
from personal_event_mesh.testing import load_fixture, assert_contract_compatible

event = load_fixture("monitoring-event/uptime-kuma-down.json")
assert_contract_compatible(event, "monitoring-event")
```

## Schemas

| Schema | Description |
|---|---|
| ha-automation | Home automation events |
| monitoring-event | Infrastructure monitoring alerts |
| text-event | Plain text fallback |
| roadmap-event | Roadmap lifecycle events |
| deploy-event | Structured deploy notifications |
| deal-alert | Price drop alerts |
| capability-report | GET /capabilities response |

## Adding a new event type

1. Add schema: `schemas/new-event.schema.json`
2. Add fixture: `fixtures/new-event/example.json`
3. Run tests: `pytest tests/ -v`
4. Tag release: `git tag v0.x.0 && git push --tags`
5. Update consumers: bump pinned version

## CI for consumer repos

Add to your GitHub Actions workflow:

```yaml
jobs:
  contracts:
    uses: mmcphee624/personal-event-mesh/.github/workflows/validate-contracts.yml@v0.1.0
    with:
      mesh-version: v0.1.0
      schema-map: '{"monitoring-event/*.json": "monitoring-event", "deal-alert/*.json": "deal-alert"}'
```

## Development

```bash
pip install -e ".[dev]"
pytest tests/ -v
ruff check src/ tests/
mypy src/
```
