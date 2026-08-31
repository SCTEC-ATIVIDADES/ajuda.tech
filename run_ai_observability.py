import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", type=Path, default=ROOT_DIR / "evidence/007-devops-inteligente/ai-prompt.txt")
    parser.add_argument("--data", type=Path, default=ROOT_DIR / "evidence/007-devops-inteligente/ai-data.json")
    parser.add_argument("--output", type=Path, default=ROOT_DIR / "evidence/007-devops-inteligente/ai-response.json")
    args = parser.parse_args()
    if os.getenv("RUN_REAL_OPENROUTER") != "1":
        print("Defina RUN_REAL_OPENROUTER=1 para executar chamada real.", file=sys.stderr)
        return 2
    try:
        if os.getenv("LLM_ANALYSIS_MODEL") and not os.getenv("LLM_MODEL"):
            os.environ["LLM_MODEL"] = os.environ["LLM_ANALYSIS_MODEL"]
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ajuda_tech.settings")
        import django
        django.setup()
        from chat.services import OpenRouterClient

        prompt = args.prompt.read_text(encoding="utf-8")
        data = json.loads(args.data.read_text(encoding="utf-8"))
        client = OpenRouterClient(max_retries=0)
        content = client.chat_completion([{
            "role": "user",
            "content": prompt + "\n\nDados JSON:\n" + json.dumps(data, ensure_ascii=False),
        }])
        result = json.loads(content)
        output = {
            "executed_at": datetime.now(timezone.utc).isoformat(),
            "model": client.model,
            "analysis": result,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        temporary = args.output.with_name(f".{args.output.name}.tmp")
        temporary.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.replace(args.output)
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
