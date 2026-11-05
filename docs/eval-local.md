# Evaluating Local Fine-Tuned Models

## Pointing the harness at a newly trained checkpoint

1. Serve the checkpoint at an OpenAI-compatible endpoint (default `http://localhost:8080/v1`).
2. Update `packages/eval/config.yaml`:
   ```yaml
   provider: local
   model: your-checkpoint-name
   endpoint: http://localhost:8080/v1
   temperature: 0.0
   max_tokens: 2048
   ```
3. Run the eval as usual; the six-dimension rubric and ten seed cases are unchanged.

## Acceptance bar

- Agent-eval must pass on the local model (fail-closed) before promoting any checkpoint from staging to `models/`.
- Use `packages/eval/compare.py` to generate side-by-side diff reports against Grok.
- Weekly drift report includes local-vs-grok trend line.
- Do not weaken any existing rubric dimension or seed case.

## Sample comparison

If local endpoint is reachable, run `python -m packages.eval.compare`. Otherwise, blocked on uni-02 (local server not available in this environment).

Hash-chained audit trail and Julian-grader / Rowan-Keiko acceptance flow remain in effect.
