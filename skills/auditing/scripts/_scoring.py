"""Shared scoring utilities for auditing scripts."""

from collections import Counter


def compute_baseline_score(findings, cap_per_id=True):
    """Deterministic baseline: 10 minus penalties for critical/warning findings.

    Both deterministic and suspicious findings affect scoring. Suspicious
    findings include a confidence field in JSON for CI to make fine-grained
    decisions.

    When cap_per_id is True (plugin/workflow mode), warnings from the same
    check-ID are capped at -3 penalty per ID to prevent a single conceptual
    gap (e.g. missing prompt files for N skills) from producing N × -1
    multiplicative punishment. When False (skill mode), each warning counts
    as -1 without capping.
    """
    critical = sum(1 for f in findings
                   if f.get("severity", f.get("risk", "info")) == "critical")
    if cap_per_id:
        warning_checks = Counter(
            f.get("check", "?") for f in findings
            if f.get("severity", f.get("risk", "info")) == "warning"
        )
        warning_penalty = sum(min(count, 3) for count in warning_checks.values())
    else:
        warning_penalty = sum(
            1 for f in findings
            if f.get("severity", f.get("risk", "info")) == "warning"
        )
    return max(0, 10 - (critical * 3 + warning_penalty))


def compute_weighted_average(scores, weights):
    """Weighted average across categories, skipping None values."""
    total_weight = 0
    weighted_sum = 0.0
    for cat, score in scores.items():
        if score is None:
            continue
        w = weights.get(cat, 1)
        weighted_sum += score * w
        total_weight += w
    return round(weighted_sum / total_weight, 1) if total_weight else 0.0
