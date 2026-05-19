"""Classifier agent evaluation run."""

import os
from pathlib import Path

from azure.ai.evaluation import (
    F1ScoreEvaluator,
    evaluate,
    AzureOpenAIModelConfiguration,
)

from evaluators import ClassificationAccuracyEvaluator


def run_classifier_evaluation(evaluation_name: str, run_name: str) -> dict:
    """Run evaluation for the classifier agent."""
    eval_data_path = Path(__file__).parent / "eval_dataset.jsonl"
    if not eval_data_path.exists():
        from generate_dataset import generate_eval_dataset
        generate_eval_dataset()

    model_config = AzureOpenAIModelConfiguration(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ.get("AZURE_OPENAI_API_KEY", ""),
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2025-01-01-preview"),
        azure_deployment=os.environ.get("EVAL_MODEL_DEPLOYMENT", "gpt-4.1-mini"),
    )

    evaluators = {
        "classification": ClassificationAccuracyEvaluator(),
        "f1_score": F1ScoreEvaluator(),
    }

    print(f"  Running classifier evaluation ({eval_data_path.name})...")
    result = evaluate(
        evaluation_name=evaluation_name,
        run_name=run_name,
        data=str(eval_data_path),
        evaluators=evaluators,
        evaluator_config={
            "default": {
                "column_mapping": {
                    "query": "${data.query}",
                    "response": "${data.ground_truth}",
                    "ground_truth": "${data.ground_truth}",
                }
            }
        },
        output_path=str(Path(__file__).parent / "classifier_results.json"),
    )

    metrics = result.get("metrics", {})
    _print_metrics(metrics)
    return metrics


def _print_metrics(metrics: dict) -> None:
    for key, value in sorted(metrics.items()):
        if isinstance(value, float):
            print(f"    {key}: {value:.4f}")
