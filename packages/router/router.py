"""Model router for Grok Bots: routes prompts to Grok or local backend based on YAML rules.

Supports shadow mode, promotion flags, fail-closed fallback, and compliance audit.
"""

import os
import yaml
import time
import hashlib
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

# Placeholder for actual adapters
class BaseAdapter:
    def complete(self, prompt: str, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError

class GrokAdapter(BaseAdapter):
    def complete(self, prompt: str, **kwargs) -> Dict[str, Any]:
        # Existing Grok path - unchanged
        start = time.time()
        # Simulate or call actual Grok
        response = {"content": "Grok response placeholder", "model": "grok"}
        latency = time.time() - start
        return {
            "response": response,
            "telemetry": {
                "backend": "grok",
                "latency_ms": latency * 1000,
                "tokens_prompt": len(prompt.split()),
                "tokens_completion": 10,
                "timestamp": datetime.utcnow().isoformat()
            }
        }

class LocalAdapter(BaseAdapter):
    def __init__(self, endpoint: str = "http://localhost:8080"):
        self.endpoint = endpoint

    def complete(self, prompt: str, **kwargs) -> Dict[str, Any]:
        start = time.time()
        try:
            # OpenAI-compatible call to local inference server
            # import openai or requests
            # response = client.chat.completions.create(...)
            response = {"content": "Local model response placeholder", "model": "local-ft"}
            latency = time.time() - start
            return {
                "response": response,
                "telemetry": {
                    "backend": "local",
                    "latency_ms": latency * 1000,
                    "tokens_prompt": len(prompt.split()),
                    "tokens_completion": 10,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            raise ConnectionError(f"Local endpoint unreachable: {e}")

class ModelRouter:
    def __init__(self, config_path: str = "config/routing.yaml", audit_log: str = "audit/router_audit.jsonl"):
        self.config_path = config_path
        self.audit_log = audit_log
        self.rules = {}
        self.load_config()
        self.grok = GrokAdapter()
        self.local = LocalAdapter()
        # Hot-reload setup would go here (e.g., watchdog)

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                self.rules = yaml.safe_load(f) or {}
        else:
            self.rules = {"bots": {}, "default": "grok"}

    def route(self, bot_name: str, prompt: str, task_type: Optional[str] = None) -> Dict[str, Any]:
        bot_rules = self.rules.get("bots", {}).get(bot_name, {})
        primary = bot_rules.get("primary", self.rules.get("default", "grok"))
        shadow = bot_rules.get("shadow_mode", False)
        promoted = bot_rules.get("promoted_to_local", False)

        if promoted:
            primary = "local"

        results = {}
        chosen = primary
        reason = f"rule match for {bot_name}"

        try:
            if primary == "local":
                results["local"] = self.local.complete(prompt)
                chosen = "local"
            else:
                results["grok"] = self.grok.complete(prompt)
                chosen = "grok"

            if shadow and primary == "grok":
                try:
                    results["local"] = self.local.complete(prompt)
                except Exception:
                    results["local"] = {"error": "local unreachable in shadow"}

            # Fail-closed: if local fails and was primary, fall back
            if chosen == "local" and "error" in results.get("local", {}):
                results["grok"] = self.grok.complete(prompt)
                chosen = "grok"
                reason = "fallback: local unreachable"

        except Exception as e:
            # Always fall back to Grok
            results["grok"] = self.grok.complete(prompt)
            chosen = "grok"
            reason = f"fallback due to error: {e}"

        # Return the chosen response
        response = results[chosen]["response"]
        telemetry = results[chosen]["telemetry"]

        # Audit log with hash-chain
        self._audit(bot_name, chosen, reason, telemetry, results.get("local"))

        return {
            "response": response,
            "telemetry": telemetry,
            "backend": chosen,
            "reason": reason,
            "shadow_results": results.get("local") if shadow else None
        }

    def _audit(self, bot: str, backend: str, reason: str, telemetry: Dict, local_result: Optional[Dict]):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "bot": bot,
            "backend": backend,
            "reason": reason,
            "latency": telemetry.get("latency_ms"),
            "tokens": telemetry.get("tokens_prompt", 0) + telemetry.get("tokens_completion", 0),
            "local_shadow": local_result is not None
        }
        # Simple hash-chain: hash of previous + current
        prev_hash = "0" * 64
        if os.path.exists(self.audit_log):
            with open(self.audit_log, 'r') as f:
                lines = f.readlines()
                if lines:
                    prev = json.loads(lines[-1])
                    prev_hash = prev.get("hash", prev_hash)
        entry_str = json.dumps(entry, sort_keys=True)
        entry["hash"] = hashlib.sha256((prev_hash + entry_str).encode()).hexdigest()
        with open(self.audit_log, 'a') as f:
            f.write(json.dumps(entry) + "\n")

# Example usage
if __name__ == "__main__":
    router = ModelRouter()
    result = router.route("Ava Renner", "Lead the program")
    print(result)
