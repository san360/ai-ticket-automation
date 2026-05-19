"""Evaluation runner for HR ticket automation agents.

Evaluation names: "classifier-agent-eval", "message-agent-eval", "document-analysis-agent-eval"
Run name: <branch-name> (e.g. "main", "feature-x")
Runs separate evaluations per agent.
"""

import json
import os
import sys
from pathlib import Path

from quality_gates import check_quality_gates
from run_classifier_eval import run_classifier_evaluation
from run_document_eval import run_document_analysis_evaluation
from run_message_eval import run_message_evaluation


CLASSIFIER_EVAL_NAME = "classifier-agent-eval"
MESSAGE_EVAL_NAME = "message-agent-eval"
DOCUMENT_EVAL_NAME = "document-analysis-agent-eval"


def get_run_name() -> str:
    """Build run name from branch: e.g. 'main', 'feature-x'."""
    branch = os.environ.get("BRANCH_NAME", os.environ.get("GITHUB_HEAD_REF", "local"))
    branch = branch.replace("refs/heads/", "").replace("/", "-")
    return branch


def main():
    """Execute evaluation for all agents."""
    results = {}
    run_name = get_run_name()

    print(f"\n{'='*60}")
    print(f"EVALUATIONS: {CLASSIFIER_EVAL_NAME}, {MESSAGE_EVAL_NAME}, {DOCUMENT_EVAL_NAME}")
    print(f"RUN: {run_name}")
    print(f"{'='*60}")

    # Classifier Agent evaluation
    print(f"\n--- {CLASSIFIER_EVAL_NAME} ---")
    classifier_metrics = run_classifier_evaluation(CLASSIFIER_EVAL_NAME, run_name)
    results["classifier"] = classifier_metrics

    # Message Agent evaluation
    print(f"\n--- {MESSAGE_EVAL_NAME} ---")
    message_metrics = run_message_evaluation(MESSAGE_EVAL_NAME, run_name)
    results["message"] = message_metrics

    # Document Analysis Agent evaluation
    print(f"\n--- {DOCUMENT_EVAL_NAME} ---")
    document_metrics = run_document_analysis_evaluation(DOCUMENT_EVAL_NAME, run_name)
    results["document_analysis"] = document_metrics

    # Write combined summary
    summary_path = Path(__file__).parent / "eval_summary.json"
    summary = {
        "evaluation_names": [CLASSIFIER_EVAL_NAME, MESSAGE_EVAL_NAME, DOCUMENT_EVAL_NAME],
        "runs": results,
        "overall_pass": all(
            check_quality_gates(m, agent, verbose=False)
            for agent, m in results.items()
            if m  # skip empty results
        ),
    }
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nResults saved to: {summary_path}")

    # Final gate check with output
    all_pass = True
    for agent, metrics in results.items():
        if metrics and not check_quality_gates(metrics, agent, verbose=True):
            all_pass = False

    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
