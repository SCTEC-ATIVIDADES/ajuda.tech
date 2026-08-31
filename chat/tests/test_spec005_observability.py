import json
import logging
from unittest.mock import patch

import pytest
from django.test import Client, override_settings

from chat.observability import (
    ExecutionTimeout,
    analyze_events,
    clear_metrics,
    emit_event,
    execution_context,
    metrics_snapshot,
)


def test_runtime_logs_and_metrics_share_execution_ids(caplog):
    clear_metrics()
    caplog.set_level(logging.INFO, logger="chat.observability")
    with execution_context("trace-runtime", "run-runtime"):
        emit_event("request", "start", "started")
        emit_event("catalog.notebook", "complete", "ok", duration_ms=4.5)
    logs = [json.loads(record.message) for record in caplog.records if record.name == "chat.observability"]
    metrics = metrics_snapshot()
    assert logs
    assert {(item["trace_id"], item["run_id"]) for item in logs} == {("trace-runtime", "run-runtime")}
    assert {(item["trace_id"], item["run_id"]) for item in metrics} == {("trace-runtime", "run-runtime")}
    assert any(item["stage"] == "catalog.notebook" and item["duration_ms"] == 4.5 for item in metrics)
    clear_metrics()


def test_analysis_rejects_invalid_correlation_event():
    with pytest.raises(ValueError, match="campos obrigatórios"):
        analyze_events([{"trace_id": "t"}])
    with pytest.raises(ValueError, match="IDs"):
        analyze_events([{
            "timestamp": "2026-01-01T00:00:00Z", "trace_id": "", "run_id": "r",
            "stage": "request", "event": "start", "status": "started",
            "duration_ms": 0, "error_type": None,
        }])


def test_graph_state_ids_are_used_without_outer_context():
    from chat.agent.graph import build_graph

    with patch("chat.agent.nodes._call_llm", side_effect=["saudacao", "Olá"]):
        clear_metrics()
        result = build_graph().compile().invoke({
            "messages": [{"role": "user", "content": "Oi"}],
            "trace_id": "trace-state",
            "run_id": "run-state",
        })
    assert result["stage"] == "greet"
    assert {(item["trace_id"], item["run_id"]) for item in metrics_snapshot()} == {("trace-state", "run-state")}
    clear_metrics()


@override_settings(AGENT_TIMEOUT=0.001)
def test_agent_timeout_returns_without_retry():
    client = Client()
    with patch("chat.views._get_agent_graph") as graph:
        graph.return_value.invoke.side_effect = ExecutionTimeout("deadline")
        response = client.post(
            "/agent/send/",
            data=json.dumps({"message": "Quero estudar"}),
            content_type="application/json",
        )
    assert response.status_code == 503
    assert "tempo limite" in response.json()["error"]
    assert graph.return_value.invoke.call_count == 1
