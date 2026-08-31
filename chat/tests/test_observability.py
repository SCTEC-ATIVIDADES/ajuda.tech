import json
from pathlib import Path

import requests as req_module

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


def test_real_http_events_keep_execution_correlation():
    from unittest.mock import patch
    from chat.services import OpenRouterClient
    from chat.tests.test_services import make_chat_response, make_mock_response

    clear_metrics()
    with execution_context("trace-http", "run-http"):
        with patch("chat.services.requests.post", side_effect=[req_module.exceptions.Timeout(), make_mock_response(200, make_chat_response("ok"))]):
            with patch("chat.services.time.sleep"):
                assert OpenRouterClient(api_key="test-key").chat_completion([{"role": "user", "content": "teste"}]) == "ok"

    records = metrics_snapshot()
    assert records
    assert {(record["trace_id"], record["run_id"]) for record in records} == {("trace-http", "run-http")}
    assert {record["event"] for record in records} >= {"timeout", "retry"}


def test_fixture_analysis_is_deterministic():
    events = json.loads((FIXTURES / "observability_failure_fixture.json").read_text())
    expected = analyze_events(events)
    assert analyze_events(events) == expected
    assert expected["probable_cause"] == "TimeoutError"
    assert expected["durations_ms"]["catalog"] == 1000
