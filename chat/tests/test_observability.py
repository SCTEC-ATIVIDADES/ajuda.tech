import json
from pathlib import Path

from chat.observability import analyze_events, clear_metrics, emit_event, execution_context, metrics_snapshot


FIXTURES = Path(__file__).parent


def test_schema_ids_and_correlated_metric():
    clear_metrics()
    with execution_context("trace-test", "run-test"):
        record = emit_event("test", "complete", "ok", duration_ms=2)
    assert set(record) == {"timestamp", "trace_id", "run_id", "stage", "event", "status", "duration_ms", "error_type"}
    assert record["trace_id"] == "trace-test"
    assert metrics_snapshot()[0]["trace_id"] == "trace-test"
    json.dumps(record)


def test_fixture_analysis_is_deterministic():
    events = json.loads((FIXTURES / "observability_failure_fixture.json").read_text())
    expected = analyze_events(events)
    assert analyze_events(events) == expected
    assert expected["probable_cause"] == "TimeoutError"
    assert expected["durations_ms"]["catalog"] == 1000
