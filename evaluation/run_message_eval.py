"""Message agent evaluation run."""

import os
from pathlib import Path

from azure.ai.evaluation import (
    CoherenceEvaluator,
    RelevanceEvaluator,
    evaluate,
    AzureOpenAIModelConfiguration,
)


def run_message_evaluation(evaluation_name: str, run_name: str) -> dict:
    """Run evaluation for the message generation agent."""
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
        "relevance": RelevanceEvaluator(model_config),
        "coherence": CoherenceEvaluator(model_config),
    }

    print(f"  Running message agent evaluation ({eval_data_path.name})...")
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
                    "context": "${data.context}",
                }
            }
        },
        output_path=str(Path(__file__).parent / "message_results.json"),
    )

    metrics = result.get("metrics", {})
    _print_metrics(metrics)
    return metrics


def _print_metrics(metrics: dict) -> None:
    for key, value in sorted(metrics.items()):
        if isinstance(value, float):
            print(f"    {key}: {value:.4f}")
