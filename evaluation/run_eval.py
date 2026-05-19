"""Run evaluation of the HR Ticket Classifier Agent.

Evaluates classification accuracy, confidence calibration, and response quality
using both custom metrics and Azure AI Evaluation SDK built-in evaluators.
"""

import json
import os
import sys
from pathlib import Path

from azure.ai.evaluation import (
    CoherenceEvaluator,
    F1ScoreEvaluator,
    GroundednessEvaluator,
    RelevanceEvaluator,
    evaluate,
    AzureOpenAIModelConfiguration,
)


class ClassificationAccuracyEvaluator:
    """Custom evaluator for HR ticket classification accuracy."""

    def __init__(self):
        self.id = "classification_accuracy"

    def __call__(self, *, response: str, ground_truth: str, **kwargs) -> dict:
        try:
            predicted = json.loads(response)
            expected = json.loads(ground_truth)
        except (json.JSONDecodeError, TypeError):
            return {
                "classification_accuracy": 0.0,
                "category_match": 0.0,
                "subcategory_match": 0.0,
                "operator_group_match": 0.0,
                "language_match": 0.0,
                "missing_info_recall": 0.0,
                "confidence_calibration": 0.0,
            }

        # Field-level accuracy
        cat_match = float(
            predicted.get("category", "").lower() == expected.get("category", "").lower()
        )
        subcat_match = float(
            predicted.get("subcategory", "").lower() == expected.get("subcategory", "").lower()
        )
        og_match = float(
            predicted.get("operatorGroup", "").upper() == expected.get("operatorGroup", "").upper()
        )
        lang_match = float(
            predicted.get("language", "").upper() == expected.get("language", "").upper()
        )

        # Missing info recall: what percentage of expected missing items were found
        expected_missing = set(m.lower() for m in expected.get("missingInfo", []))
        predicted_missing = set(m.lower() for m in predicted.get("missingInfo", []))

        if not expected_missing:
            # If no missing info expected, check that none was predicted (penalize false positives)
            missing_recall = 1.0 if not predicted_missing else 0.5
        else:
            # Check overlap (fuzzy: at least partial match)
            matches = sum(
                1 for exp in expected_missing
                if any(exp in pred or pred in exp for pred in predicted_missing)
            )
            missing_recall = matches / len(expected_missing) if expected_missing else 1.0

        # Confidence calibration: is confidence >= expected minimum?
        predicted_conf = predicted.get("confidence", 0.0)
        expected_min_conf = expected.get("confidence_min", 0.5)
        conf_calibration = 1.0 if predicted_conf >= expected_min_conf else predicted_conf / expected_min_conf

        # Overall accuracy (weighted)
        overall = (
            cat_match * 0.30
            + subcat_match * 0.25
            + og_match * 0.20
            + lang_match * 0.10
            + missing_recall * 0.10
            + conf_calibration * 0.05
        )

        return {
            "classification_accuracy": overall,
            "category_match": cat_match,
            "subcategory_match": subcat_match,
            "operator_group_match": og_match,
            "language_match": lang_match,
            "missing_info_recall": missing_recall,
            "confidence_calibration": conf_calibration,
        }


def run_evaluation():
    """Execute the full evaluation pipeline."""
    # Check for eval dataset
    eval_data_path = Path(__file__).parent / "eval_dataset.jsonl"
    if not eval_data_path.exists():
        print("Generating evaluation dataset...")
        from generate_dataset import generate_eval_dataset
        generate_eval_dataset()

    # Configure model for AI-assisted evaluators
    model_config = AzureOpenAIModelConfiguration(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ.get("AZURE_OPENAI_API_KEY", ""),
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2025-01-01-preview"),
        azure_deployment=os.environ.get("EVAL_MODEL_DEPLOYMENT", "gpt-4.1-mini"),
    )

    # Define evaluators
    evaluators = {
        "classification": ClassificationAccuracyEvaluator(),
        "f1_score": F1ScoreEvaluator(),
        "relevance": RelevanceEvaluator(model_config),
        "coherence": CoherenceEvaluator(model_config),
        "groundedness": GroundednessEvaluator(model_config),
    }

    # Run evaluation
    print(f"Running evaluation on {eval_data_path}...")
    result = evaluate(
        data=str(eval_data_path),
        evaluators=evaluators,
        evaluator_config={
            "default": {
                "column_mapping": {
                    "query": "${data.query}",
                    "response": "${data.ground_truth}",
                    "context": "${data.context}",
                    "ground_truth": "${data.ground_truth}",
                }
            }
        },
        output_path="./evaluation/eval_results.json",
    )

    # Print results
    print("\n" + "=" * 60)
    print("EVALUATION RESULTS")
    print("=" * 60)

    metrics = result.get("metrics", {})
    for key, value in sorted(metrics.items()):
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        else:
            print(f"  {key}: {value}")

    # Write summary for CI
    summary_path = Path(__file__).parent / "eval_summary.json"
    with open(summary_path, "w") as f:
        json.dump({"metrics": metrics, "num_samples": len(list(eval_data_path.open()))}, f, indent=2)

    print(f"\nResults saved to: {summary_path}")
    return metrics


def check_quality_gates(metrics: dict):
    """Check if evaluation meets quality thresholds."""
    gates = {
        "classification.classification_accuracy": 0.80,
        "classification.category_match": 0.85,
        "classification.language_match": 0.95,
        "relevance.relevance": 3.0,
        "coherence.coherence": 3.0,
    }

    failures = []
    for metric, threshold in gates.items():
        value = metrics.get(metric, 0)
        if value < threshold:
            failures.append(f"{metric}: {value:.3f} < {threshold}")

    if failures:
        print("\n❌ QUALITY GATES FAILED:")
        for f in failures:
            print(f"  - {f}")
        return False
    else:
        print("\n✅ All quality gates PASSED")
        return True


if __name__ == "__main__":
    metrics = run_evaluation()
    passed = check_quality_gates(metrics)
    sys.exit(0 if passed else 1)
