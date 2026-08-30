"""Eventos estruturados e contexto de execução do agente."""

from __future__ import annotations

import contextvars
import json
import logging
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4

logger = logging.getLogger("chat.observability")

_REQUIRED_FIELDS = (
    "timestamp", "trace_id", "run_id", "stage", "event", "status",
    "duration_ms", "error_type",
)
_context = contextvars.ContextVar("execution_context", default=None)
_metrics: dict[tuple[str, str, str, str, str], dict[str, float | int]] = {}
_metrics_lock = Lock()


class ExecutionTimeout(TimeoutError):
    pass


def new_id() -> str:
    return str(uuid4())


def current_context() -> dict:
    return _context.get() or {}


def remaining_seconds() -> float | None:
    deadline = current_context().get("deadline")
    if deadline is None:
        return None
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise ExecutionTimeout("tempo total da execução excedido")
    return remaining


@contextmanager
def execution_context(trace_id: str | None = None, run_id: str | None = None, timeout: float | None = None):
    context = {
        "trace_id": trace_id or new_id(),
        "run_id": run_id or new_id(),
        "deadline": time.monotonic() + timeout if timeout else None,
    }
    token = _context.set(context)
    try:
        yield context
    finally:
        _context.reset(token)


def _error_type(error) -> str | None:
    return type(error).__name__ if error else None


def emit_event(stage: str, event: str, status: str, *, duration_ms: float = 0, error=None) -> dict:
    context = current_context()
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "trace_id": context.get("trace_id", ""),
        "run_id": context.get("run_id", ""),
        "stage": str(stage)[:100],
        "event": str(event)[:50],
        "status": str(status)[:50],
        "duration_ms": round(max(float(duration_ms), 0), 2),
        "error_type": _error_type(error),
    }
    with _metrics_lock:
        key = (record["trace_id"], record["run_id"], record["stage"], record["event"], record["status"])
        metric = _metrics.setdefault(key, {"count": 0, "duration_ms": 0.0})
        metric["count"] += 1
        metric["duration_ms"] += record["duration_ms"]
    logger.info(json.dumps(record, ensure_ascii=False, sort_keys=True))
    return record


def analyze_events(events: list[dict]) -> dict:
    missing = [field for event in events for field in _REQUIRED_FIELDS if field not in event]
    if missing:
        raise ValueError("evento sem campos obrigatórios")
    if any(not event["trace_id"] or not event["run_id"] for event in events):
        raise ValueError("evento sem IDs de correlação")
    ordered = sorted(enumerate(events), key=lambda pair: (pair[1].get("timestamp", ""), pair[0]))
    records = [item for _, item in ordered]
    ids = {(item.get("trace_id"), item.get("run_id")) for item in records}
    if len(ids) > 1:
        raise ValueError("eventos de execuções diferentes não podem ser correlacionados")
    failures = [item for item in records if item.get("status") == "error"]
    durations = {}
    for item in records:
        if item.get("event") == "complete":
            stage = item["stage"]
            durations[stage] = durations.get(stage, 0) + item.get("duration_ms", 0)
    slowest = max(durations.items(), key=lambda item: item[1]) if durations else (None, 0)
    return {
        "trace_id": records[0].get("trace_id") if records else None,
        "run_id": records[0].get("run_id") if records else None,
        "stages": [item["stage"] for item in records if item.get("event") == "start"],
        "durations_ms": durations,
        "slowest_stage": slowest[0],
        "failures": [{"stage": item["stage"], "error_type": item.get("error_type")} for item in failures],
        "probable_cause": failures[0].get("error_type") if failures else None,
    }


def metrics_snapshot() -> list[dict]:
    with _metrics_lock:
        return [
            {
                "trace_id": trace_id,
                "run_id": run_id,
                "stage": stage,
                "event": event,
                "status": status,
                "count": metric["count"],
                "duration_ms": round(float(metric["duration_ms"]), 2),
            }
            for (trace_id, run_id, stage, event, status), metric in sorted(_metrics.items())
        ]


def clear_metrics() -> None:
    with _metrics_lock:
        _metrics.clear()


def check_deadline() -> None:
    remaining_seconds()


def dependency_timeout(default: float) -> float:
    remaining = remaining_seconds()
    return default if remaining is None else min(float(default), remaining)


@contextmanager
def stage(stage: str):
    started = time.perf_counter()
    emit_event(stage, "start", "started")
    try:
        check_deadline()
        yield
    except Exception as exc:
        emit_event(stage, "complete", "error", duration_ms=(time.perf_counter() - started) * 1000, error=exc)
        raise
    else:
        emit_event(stage, "complete", "ok", duration_ms=(time.perf_counter() - started) * 1000)
