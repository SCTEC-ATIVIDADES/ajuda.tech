import json
import runpy
from pathlib import Path


FIXTURE = Path(__file__).parent / "observability_fixture.json"


def test_log_analysis_reports_anomaly_trend_and_risk():
    module = runpy.run_path("analyze_observability.py")
    events = json.loads(FIXTURE.read_text(encoding="utf-8"))
    result = module["analyze_log"](events)

    assert result["anomalies"] == [
        {"stage": "catalog", "duration_ms": 700, "threshold_ms": 500},
        {"stage": "catalog", "duration_ms": 900, "threshold_ms": 500},
    ]
    assert result["trend"]["catalog"]["change_percent"] == 28.57
    assert result["trend"]["catalog"]["uncertainty"].startswith("high:")
    assert result["risk"] == "medium"
    assert result["ai_analysis"]["status"] == "not_called"
