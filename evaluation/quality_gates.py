"""Quality gate checks for agent evaluations."""

CLASSIFIER_GATES = {
    "classification.classification_accuracy": 0.80,
    "classification.category_match": 0.85,
    "classification.language_match": 0.95,
}

MESSAGE_GATES = {
    "relevance.relevance": 3.0,
    "coherence.coherence": 3.0,
}


def check_quality_gates(metrics: dict, agent: str, verbose: bool = True) -> bool:
    """Check if evaluation metrics meet quality thresholds for given agent."""
    gates = CLASSIFIER_GATES if agent == "classifier" else MESSAGE_GATES
    failures = []

    for metric, threshold in gates.items():
        value = metrics.get(metric, 0)
        if value < threshold:
            failures.append(f"{metric}: {value:.3f} < {threshold}")

    if verbose:
        if failures:
            print(f"\n❌ QUALITY GATES FAILED ({agent} agent):")
            for f in failures:
                print(f"  - {f}")
        else:
            print(f"\n✅ All quality gates PASSED ({agent} agent)")

    return len(failures) == 0
