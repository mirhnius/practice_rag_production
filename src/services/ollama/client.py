"""
Week 5 — Ollama LLM client.

Talks to a local Ollama server (default http://localhost:11434) to
generate answers from retrieved context.
Docs: https://github.com/ollama/ollama/blob/main/docs/api.md
"""

from collections.abc import Iterator

import requests


class OllamaClient:
    def __init__(self, host: str, model: str, timeout: int = 300) -> None:
        self.host = host
        self.model = model
        self.timeout = timeout

    def generate(self, prompt: str) -> str:
        """A single non-streaming completion.

        TODO:
        - response = requests.post(f"{self.host}/api/generate",
              json={"model": self.model, "prompt": prompt, "stream": False},
              timeout=self.timeout)
        - response.raise_for_status()
        - return response.json()["response"].strip()
        """
        raise NotImplementedError

    def generate_stream(self, prompt: str) -> Iterator[str]:
        """Yield response text incrementally as Ollama generates it.

        TODO:
        - response = requests.post(f"{self.host}/api/generate",
              json={"model": self.model, "prompt": prompt, "stream": True},
              timeout=self.timeout, stream=True)
        - for line in response.iter_lines():
              if not line: continue
              chunk = json.loads(line)
              yield chunk.get("response", "")
              if chunk.get("done"): break
        """
        raise NotImplementedError
