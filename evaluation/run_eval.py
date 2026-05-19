"""Evaluation runner for HR ticket automation agents.

Evaluation name: "agents"
Run name: <branch-name>/<agent-name> (e.g. "main/classifier", "feature-x/message")
Runs separate evaluations per agent.
"""

import json
import os
import sys
from pathlib import Path

from quality_gates import check_quality_gates
from run_classifier_eval import run_classifier_evaluation
from run_message_eval import run_message_evaluation


EVALUATION_NAME = "agents"


def get_run_name(agent_name: str) -> str:
    """Build run name from branch + agent: e.g. 'main/classifier'."""
    branch = os.environ.get("BRANCH_NAME", os.environ.get("GITHUB_HEAD_REF", "local"))
    branch = branch.replace("refs/heads/", "").replace("/", "-")
    return f"{branch}/{agent_name}"


def main():
    """Execute evaluation for all agents."""
    results = {}

    print(f"\n{'='*60}")
    print(f"EVALUATION: {EVALUATION_NAME}")
    print(f"{'='*60}")

    # Classifier Agent evaluation
    classifier_run = get_run_name("classifier")
    print(f"\n--- Run: {classifier_run} ---")
    classifier_metrics = run_classifier_evaluation(EVALUATION_NAME, classifier_run)
    results["classifier"] = classifier_metrics

    # Message Agent evaluation
    message_run = get_run_name("message")
    print(f"\n--- Run: {message_run} ---")
    message_metrics = run_message_evaluation(EVALUATION_NAME, message_run)
    results["message"] = message_metrics

    # Write combined summary
    summary_path = Path(__file__).parent / "eval_summary.json"
    summary = {
        "evaluation_name": EVALUATION_NAME,
        "runs": results,
        "overall_pass": all(
            check_quality_gates(m, agent, verbose=False)
            for agent, m in results.items()
        ),
    }
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nResults saved to: {summary_path}")

    # Final gate check with output
    all_pass = True
    for agent, metrics in results.items():
        if not check_quality_gates(metrics, agent, verbose=True):
            all_pass = False

    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
