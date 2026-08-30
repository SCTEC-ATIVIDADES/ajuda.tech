import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests

PROMPT_PATH = Path("evidence/007-devops-inteligente/ai-prompt.txt")
DATA_PATH = Path("evidence/007-devops-inteligente/ai-data.json")
OUTPUT_PATH = Path("evidence/007-devops-inteligente/ai-response.json")


def main():
    prompt = PROMPT_PATH.read_text(encoding="utf-8")
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    payload = {
        "model": os.environ.get("LLM_ANALYSIS_MODEL", os.environ.get("LLM_MODEL", "deepseek/deepseek-v4-flash:free")),
        "messages": [
            {"role": "system", "content": "Você analisa observabilidade. Responda somente JSON válido."},
            {"role": "user", "content": prompt + "\n\nDados JSON:\n" + json.dumps(data, ensure_ascii=False)},
        ],
        "temperature": 0,
        "response_format": {"type": "json_object"},
    }
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.environ['LLM_API_KEY']}", "Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    response_data = response.json()
    if "choices" not in response_data:
        raise RuntimeError("OpenRouter não retornou choices")
    content = response_data["choices"][0]["message"]["content"]
    result = json.loads(content)
    OUTPUT_PATH.write_text(json.dumps({
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "model": payload["model"],
        "analysis": result,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
