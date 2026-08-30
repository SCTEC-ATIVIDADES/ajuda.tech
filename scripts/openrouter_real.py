#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))


def load_env():
    try:
        lines = (ROOT_DIR / ".env").read_text(encoding="utf-8").splitlines()
    except OSError:
        return
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, separator, value = line.partition("=")
        if separator and key.strip() and key.strip() not in os.environ:
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            os.environ[key.strip()] = value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--expect", default="OK")
    args = parser.parse_args()
    load_env()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ajuda_tech.settings")
    if os.getenv("RUN_REAL_OPENROUTER") != "1":
        print("Defina RUN_REAL_OPENROUTER=1 para executar chamada real.", file=sys.stderr)
        return 2
    try:
        import django
        django.setup()
        from chat.services import OpenRouterClient

        model = os.getenv("LLM_MODEL", "configuração padrão")
        print(f"Modelo: {model}", file=sys.stderr)
        response = OpenRouterClient(max_retries=0).chat_completion(
            [{"role": "user", "content": "Responda apenas OK."}]
        )
        if not isinstance(response, str) or not response.strip():
            raise ValueError("Resposta vazia do OpenRouter.")
        if response.strip() != args.expect:
            raise ValueError(f"Resposta inesperada: esperado {args.expect!r}.")
    except Exception as error:
        print(str(error), file=sys.stderr)
        return 1
    print(response.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
