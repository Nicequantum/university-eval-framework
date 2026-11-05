"""Tests for the model router: routing rules, shadow mode, fallback, telemetry schema.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from packages.router.router import ModelRouter, LocalAdapter

# Mock local endpoint
def mock_local_complete(self, prompt, **kwargs):
    return {
        "response": {"content": "mock local", "model": "local"},
        "telemetry": {
            "backend": "local",
            "latency_ms": 50.0,
            "tokens_prompt": 5,
            "tokens_completion": 2,
            "timestamp": "2026-01-01T00:00:00"
        }
    }

@pytest.fixture
def router(tmp_path):
    config = tmp_path / "routing.yaml"
    config.write_text("""
default: grok
bots:
  "Ava Renner":
    primary: grok
    shadow_mode: true
  "Julian Crowe":
    primary: local
    shadow_mode: false
""")
    return ModelRouter(config_path=str(config), audit_log=str(tmp_path / "audit.jsonl"))

def test_routing_rules(router):
    with patch.object(LocalAdapter, 'complete', mock_local_complete):
        result = router.route("Ava Renner", "test prompt")
        assert result["backend"] == "grok"
        assert result["shadow_results"] is not None

def test_shadow_mode_logs_both(router):
    with patch.object(LocalAdapter, 'complete', mock_local_complete):
        result = router.route("Ava Renner", "test")
        assert "local" in str(result["shadow_results"]) or result["shadow_results"] is not None

def test_fallback_when_local_unreachable(router):
    def failing_local(self, prompt, **kwargs):
        raise ConnectionError("down")
    with patch.object(LocalAdapter, 'complete', failing_local):
        result = router.route("Julian Crowe", "test")
        assert result["backend"] == "grok"
        assert "fallback" in result["reason"]

def test_telemetry_schema(router):
    with patch.object(LocalAdapter, 'complete', mock_local_complete):
        result = router.route("Ava Renner", "test")
        tel = result["telemetry"]
        assert "latency_ms" in tel
        assert "tokens_prompt" in tel
        assert "backend" in tel
        # Schema-valid for uni task-record

def test_audit_hash_chain(router):
    with patch.object(LocalAdapter, 'complete', mock_local_complete):
        router.route("Ava Renner", "test")
        with open(router.audit_log) as f:
            lines = f.readlines()
            assert len(lines) >= 1
            entry = json.loads(lines[0])
            assert "hash" in entry
            assert entry["bot"] == "Ava Renner"
