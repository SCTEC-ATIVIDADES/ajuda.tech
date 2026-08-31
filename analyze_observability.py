import argparse
import json
import sys
from pathlib import Path

from chat.observability import analyze_events

ANOMALY_THRESHOLD_MS = 500
MIN_TREND_POINTS = 2
RISK_LEVELS = {"low": 0, "medium": 1, "high": 2}


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


def _load_events(path: Path) -> list[dict]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"não foi possível ler JSON de eventos: {exc}") from exc
    if not isinstance(value, list) or not value:
        raise ValueError("events file must contain non-empty JSON array")
    if any(not isinstance(event, dict) for event in value):
        raise ValueError("events array must contain JSON objects")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("events", type=Path)
    parser.add_argument("--fail-on-risk", choices=tuple(RISK_LEVELS), default=None)
    args = parser.parse_args()
    try:
        result = analyze_log(_load_events(args.events))
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    if args.fail_on_risk and RISK_LEVELS[result["risk"]] >= RISK_LEVELS[args.fail_on_risk]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
