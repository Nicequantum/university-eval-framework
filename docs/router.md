# Model Router for Grok Bots

## Overview
The model router (`packages/router/router.py`) sits between bot prompts and model backends (Grok or local fine-tuned model). It enables per-bot or per-task routing without changing production behavior in this PR.

## Routing Rules
Rules are defined in `config/routing.yaml` and are hot-reloadable.
- Per-bot: e.g., Ava Renner -> Grok (frontier reasoning)
- Julian Crowe architecture -> local (repo-specific, once promoted)
- Marcus Hale 3C language -> local (warranty corpus)
- Default: Grok

## Shadow Mode
When `shadow_mode: true` per bot:
- Prompt sent to BOTH backends
- Grok result returned to the bot (nothing breaks)
- Local result logged alongside for offline comparison by uni-03 comparison runner

This validates the local model in production without risk.

## Promotion Flag
Once shadow-mode comparison shows local matching or beating Grok on the bot's task distribution:
- Flip `promoted_to_local: true`
- Local becomes primary, Grok is fallback

## Fallback Behavior (Fail-Closed)
- If local endpoint is down (unreachable), always fall back to Grok
- Never error out a bot
- Logged in audit trail

## Compliance Audit Trail
Router decisions wired into compliance hub audit trail with hash-chain pattern:
- Which bot, which backend chosen, why (rule match), latency, tokens
- Stored in `audit/router_audit.jsonl`

## How to Add a New Bot
1. Add entry under `bots` in `config/routing.yaml`
2. Set `primary: grok`, `shadow_mode: true` initially
3. After uni-03 validation, set `promoted_to_local: true` if appropriate
4. Hot-reload picks up changes

## Dependencies
Depends on uni-02 (training scaffold) and uni-03 (eval wiring) being complete for full local model integration. Currently landing skeleton + tests; document any blockers.

## Telemetry
LocalAdapter and GrokAdapter report token usage and latency in the same shape expected by university task-record schema.
