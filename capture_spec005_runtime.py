import json
import logging
import os
import sys
from pathlib import Path
from unittest.mock import patch

ROOT_DIR = Path(__file__).resolve().parent
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ajuda_tech.settings")
sys.path.insert(0, str(ROOT_DIR))

import django
from django.test import Client, override_settings

from chat.observability import clear_metrics, metrics_snapshot


class EventHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.events = []

    def emit(self, record):
        try:
            event = json.loads(record.getMessage())
        except json.JSONDecodeError:
            return
        if event.get("trace_id") and event.get("run_id"):
            self.events.append(event)


def capture(path, catalog_url, llm_responses, run_name):
    handler = EventHandler()
    logger = logging.getLogger("chat.observability")
    logger.addHandler(handler)
    clear_metrics()
    try:
        with override_settings(CATALOG_API_URL=catalog_url, ALLOWED_HOSTS=["testserver"]):
            with patch("chat.agent.nodes._call_llm", side_effect=llm_responses):
                response = Client().post(
                    "/agent/send/",
                    data=json.dumps({"message": "Quero notebook para estudar por até 3000"}),
                    content_type="application/json",
                )
        if response.status_code != 200:
            raise RuntimeError(f"POST /agent/send/ retornou HTTP {response.status_code}")
        try:
            response_body = response.json()
        except ValueError as exc:
            raise RuntimeError("POST /agent/send/ não retornou JSON válido") from exc
        if not isinstance(response_body, dict) or not response_body:
            raise RuntimeError("POST /agent/send/ retornou JSON inválido")
        events = handler.events
        metrics = metrics_snapshot()
        payload = {
            "scenario": run_name,
            "http": {"status_code": response.status_code, "keys": sorted(response_body)},
            "events": events,
            "metrics": metrics,
        }
        output_path = Path(path)
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        output_path.with_name(output_path.stem + "-events.json").write_text(json.dumps(events, ensure_ascii=False, indent=2) + "\n")
        output_path.with_name(output_path.stem + "-metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n")
    finally:
        logger.removeHandler(handler)
        clear_metrics()


def main():
    django.setup()
    output = ROOT_DIR / "evidence/005-observabilidade-resiliencia"
    output.mkdir(parents=True, exist_ok=True)
    capture(
        output / "normal-runtime.json",
        "http://catalog:8080/products",
        ["dados", '{"proposito":"estudos","orcamento":3000,"mobilidade":"alta"}', "Recomendação validada", "Resposta validada"],
        "normal",
    )
    capture(
        output / "failure-runtime.json",
        "http://catalog:8080/products/error",
        ["dados", '{"proposito":"estudos","orcamento":3000,"mobilidade":"alta"}', "Recomendação com fallback", "Resposta com fallback"],
        "catalog_failure_fallback",
    )


if __name__ == "__main__":
    main()
