import requests
import json
from typing import Optional


class OllamaClient:
    """
    Minimal, production-style Ollama client
    """

    def __init__(self, model: str = "llama3.1", host: str = "http://localhost:11434"):
        self.model = model
        self.url = f"{host}/api/generate"

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 512
    ) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }

        if system:
            payload["system"] = system

        response = requests.post(self.url, json=payload)
        response.raise_for_status()

        data = response.json()
        return data.get("response", "").strip()

