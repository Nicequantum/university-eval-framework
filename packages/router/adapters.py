from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time
import httpx

class ModelAdapter(ABC):
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Return dict with 'content', 'tokens_used', 'latency_ms' """
        pass

class GrokAdapter(ModelAdapter):
    """Existing path, unchanged behavior. Placeholder for real Grok API."""
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        start = time.time()
        # Placeholder: in real system, call actual Grok
        content = f"[Grok response to: {prompt[:50]}...]"
        latency = (time.time() - start) * 1000
        return {
            "content": content,
            "tokens_used": {"prompt": 100, "completion": 50, "total": 150},
            "latency_ms": latency,
            "backend": "grok"
        }

class LocalAdapter(ModelAdapter):
    """OpenAI-compatible call to localhost:8080 or Mac Studio inference server."""
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=30.0)

    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        start = time.time()
        try:
            # OpenAI-compatible /v1/chat/completions
            payload = {
                "model": "local-fine-tuned",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": kwargs.get("temperature", 0.7),
            }
            resp = await self.client.post(f"{self.base_url}/v1/chat/completions", json=payload)
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0})
            latency = (time.time() - start) * 1000
            return {
                "content": content,
                "tokens_used": {
                    "prompt": usage.get("prompt_tokens", 0),
                    "completion": usage.get("completion_tokens", 0),
                    "total": usage.get("total_tokens", 0)
                },
                "latency_ms": latency,
                "backend": "local"
            }
        except Exception as e:
            # Fail closed handled by router
            raise ConnectionError(f"Local endpoint unreachable: {e}")

    async def close(self):
        await self.client.aclose()
