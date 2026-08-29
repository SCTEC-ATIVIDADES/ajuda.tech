import json
import sys
from pathlib import Path

from chat.observability import analyze_events

ANOMALY_THRESHOLD_MS = 500
MIN_TREND_POINTS = 2


def analyze_log(events: list[dict]) -> dict:
    base = analyze_events(events)
    complete = [event for event in events if event.get("event") == "complete"]
    durations = {}
    for event in complete:
        durations.setdefault(event["stage"], []).append(float(event.get("duration_ms", 0)))

    anomalies = [
        {"stage": event["stage"], "duration_ms": event.get("duration_ms"), "threshold_ms": ANOMALY_THRESHOLD_MS}
        for event in complete
        if float(event.get("duration_ms", 0)) > ANOMALY_THRESHOLD_MS
    ]
    trends = {}
    for stage, values in sorted(durations.items()):
        if len(values) < MIN_TREND_POINTS:
            trends[stage] = {"method": "first_to_last_percent_change", "status": "insufficient_data", "uncertainty": "high"}
            continue
        first, last = values[0], values[-1]
        change = 0 if first == 0 else round((last - first) / first * 100, 2)
        trends[stage] = {
            "method": "first_to_last_percent_change",
            "first_ms": first,
            "last_ms": last,
            "change_percent": change,
            "status": "computed",
            "uncertainty": "high: two observations; no confidence interval",
        }

    risk = "high" if base["failures"] else "medium" if anomalies else "low"
    return {
        **base,
        "anomalies": anomalies,
        "trend": trends,
        "trend_limit": "500ms anomaly threshold; fewer than 2 comparable points means insufficient_data",
        "risk": risk,
        "ai_analysis": {"status": "not_called", "reason": "external AI unavailable; deterministic gate used"},
    }


def main() -> None:
    if len(sys.argv) not in (2, 3):
        raise SystemExit("usage: python analyze_observability.py <events.json> [--fail-on-risk LEVEL]")
    path = Path(sys.argv[1])
    events = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(events, list) or not events:
        raise SystemExit("events file must contain non-empty JSON array")
    result = analyze_log(events)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    if len(sys.argv) == 3:
        if sys.argv[2] != "--fail-on-risk":
            raise SystemExit("unknown option")
        if result["risk"] in {"medium", "high"}:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
