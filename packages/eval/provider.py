"""Eval providers for Grok-backed and local models.

The six-dimension rubric and seed cases are independent of the provider.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import requests
import os
import yaml

class BaseProvider(ABC):
    @abstractmethod
    def complete(self, task_record: Dict[str, Any]) -> Dict[str, Any]:
        """Given a task record, return completion + token usage."""
        pass

class GrokProvider(BaseProvider):
    """Existing Grok-backed provider (placeholder for current implementation)."""
    def complete(self, task_record: Dict[str, Any]) -> Dict[str, Any]:
        # Placeholder: actual Grok call would go here
        return {
            "completion": "Grok response placeholder",
            "usage": {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}
        }

class LocalModelProvider(BaseProvider):
    """Provider for fine-tuned local model served at OpenAI-compatible endpoint."""
    def __init__(self, endpoint: str = "http://localhost:8080/v1", model: str = "local-model", temperature: float = 0.0, max_tokens: int = 2048):
        self.endpoint = endpoint.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def complete(self, task_record: Dict[str, Any]) -> Dict[str, Any]:
        """Call the local model endpoint."""
        prompt = task_record.get("prompt", "")
        url = f"{self.endpoint}/chat/completions"
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        try:
            resp = requests.post(url, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            choice = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0})
            return {"completion": choice, "usage": usage}
        except Exception as e:
            return {"completion": f"Error: {str(e)}", "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}, "error": str(e)}

def get_provider(config: Optional[Dict] = None) -> BaseProvider:
    """Factory based on config."""
    if config is None:
        config = {}
    provider_type = config.get("provider", "grok")
    if provider_type == "local":
        return LocalModelProvider(
            endpoint=config.get("endpoint", "http://localhost:8080/v1"),
            model=config.get("model", "local-model"),
            temperature=config.get("temperature", 0.0),
            max_tokens=config.get("max_tokens", 2048)
        )
    return GrokProvider()
