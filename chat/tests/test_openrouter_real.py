import os

import pytest

from chat.services import OpenRouterClient


@pytest.mark.integration
@pytest.mark.skipif(
    os.getenv("RUN_REAL_OPENROUTER") != "1",
    reason="Defina RUN_REAL_OPENROUTER=1 para executar o teste contra a API real",
)
def test_openrouter_real_connection():
    client = OpenRouterClient(max_retries=0)
    response = client.chat_completion([{"role": "user", "content": "Responda apenas OK."}])
    assert isinstance(response, str)
    assert response.strip()
