"""Fail-closed gate: agent-eval must pass on local model before promoting checkpoint.

Same as existing merge gate behavior.
"""

def check_local_gate(eval_results: dict) -> bool:
    """Return True only if all dimensions pass the acceptance threshold."""
    # Placeholder: integrate with existing agent-eval
    if eval_results.get("overall_pass", False):
        return True
    return False  # fail-closed

# Promotion script would call this before moving from staging to models/
