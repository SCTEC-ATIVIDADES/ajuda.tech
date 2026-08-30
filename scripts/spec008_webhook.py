#!/usr/bin/env python3
import argparse
import hashlib
import hmac
import json
import os
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent


def env_value(name, default):
    value = os.getenv(name)
    if value:
        return value
    try:
        lines = (ROOT_DIR / ".env").read_text(encoding="utf-8").splitlines()
    except OSError:
        return default
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, separator, candidate = line.partition("=")
        if separator and key.strip() == name:
            candidate = candidate.strip()
            if len(candidate) >= 2 and candidate[0] == candidate[-1] and candidate[0] in "\"'":
                candidate = candidate[1:-1]
            return candidate or default
    return default


def request(url, payload, signature=None, timeout=180):
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()
    headers = {"Content-Type": "application/json"}
    if signature:
        headers["X-Automation-Signature"] = signature
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status, response.read().decode()
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode()


def signed_request(url, payload, secret, timeout=180):
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()
    signature = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return request(url, payload, signature, timeout)


def run(target, scenario, timeout=180, app_url=None, n8n_url=None):
    event_id = f"spec008-{scenario}-{uuid.uuid4().hex[:8]}"
    message = "Preciso de um computador para estudar"
    if target == "n8n":
        url = n8n_url or env_value("N8N_URL", "http://localhost:5678/webhook/ajuda-tech")
        send = lambda payload: request(url, payload, timeout=timeout)
    else:
        url = app_url or env_value("APP_URL", "http://localhost:8001/automation/webhook/")
        secret = env_value("AUTOMATION_WEBHOOK_SECRET", "change-me")
        send = lambda payload: signed_request(url, payload, secret, timeout)

    if scenario in {"normal", "duplicate"}:
        payload = {"event_id": event_id, "message": message}
        return [send(payload)] if scenario == "normal" else [send(payload), send(payload)]
    if scenario == "invalid":
        return [send({"event_id": event_id})]
    if scenario == "signature":
        if target == "n8n":
            raise ValueError("cenário signature só existe no endpoint app")
        return [request(url, {"event_id": event_id, "message": message}, "invalid", timeout)]
    raise ValueError(f"cenário desconhecido: {scenario}")


def parse_body(body):
    try:
        value = json.loads(body)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError("resposta não é JSON válido") from exc
    if not isinstance(value, dict):
        raise ValueError("resposta JSON deve ser objeto")
    return value


def validate(target, scenario, responses):
    expected_status = {"normal": 200, "duplicate": 200, "invalid": 400, "signature": 401}[scenario]
    if any(status != expected_status for status, _ in responses):
        raise ValueError(f"status inesperado: esperado {expected_status}")
    bodies = [parse_body(body) for _, body in responses]
    if scenario == "normal" and not bodies[0].get("reply"):
        raise ValueError("resposta normal sem reply")
    if scenario == "duplicate" and bodies[1] != {"ok": True, "duplicate": True}:
        raise ValueError("resposta duplicada inesperada")
    if scenario == "invalid" and not bodies[0].get("error"):
        raise ValueError("resposta inválida sem error")
    if scenario == "signature" and not bodies[0].get("error"):
        raise ValueError("resposta de assinatura sem error")
    return bodies


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", choices=("app", "n8n"), default="n8n")
    parser.add_argument("--timeout", type=float, default=180)
    parser.add_argument("--app-url", default=None)
    parser.add_argument("--n8n-url", default=None)
    parser.add_argument("scenario", choices=("normal", "duplicate", "invalid", "signature"))
    args = parser.parse_args()
    if args.timeout <= 0:
        print("timeout deve ser positivo", file=sys.stderr)
        return 2
    try:
        responses = run(args.target, args.scenario, args.timeout, args.app_url, args.n8n_url)
        bodies = validate(args.target, args.scenario, responses)
    except (OSError, ValueError, urllib.error.URLError, UnicodeError) as error:
        print(str(error), file=sys.stderr)
        return 1
    print(json.dumps({"scenario": args.scenario, "target": args.target, "responses": [{"status": status, "body": body} for (status, _), body in zip(responses, bodies)]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
