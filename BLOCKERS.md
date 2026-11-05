# Blockers for Full Integration

- uni-02 (training scaffold): Not present in this repository. Local model training/fine-tuning infrastructure is incomplete or external.
- uni-03 (eval wiring): Evaluation harness for comparing Grok vs local on task distributions is not yet wired in this repo.

This PR lands the router skeleton, adapters interface, shadow mode, promotion flags, fail-closed fallback, compliance audit (hash-chain), docs, and tests with mock local endpoint.

No bot's production behavior changes. Grok remains the default everywhere. Shadow mode only.

Once uni-02 and uni-03 are substantially complete, promote bots via YAML config.
