"""Document analysis agent evaluation run."""

import os
from pathlib import Path

from azure.ai.evaluation import (
    RelevanceEvaluator,
    evaluate,
    AzureOpenAIModelConfiguration,
)

from evaluators import DocumentAnalysisEvaluator


def run_document_analysis_evaluation(evaluation_name: str, run_name: str) -> dict:
    """Run evaluation for the document analysis agent."""
    eval_data_path = Path(__file__).parent.parent / "agents" / "evals" / "document-analysis-golden-dataset.jsonl"
    if not eval_data_path.exists():
        print("  WARNING: Document analysis golden dataset not found. Skipping.")
        return {}

    model_config = AzureOpenAIModelConfiguration(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ.get("AZURE_OPENAI_API_KEY", ""),
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2025-01-01-preview"),
        azure_deployment=os.environ.get("EVAL_MODEL_DEPLOYMENT", "gpt-4.1-mini"),
    )

    evaluators = {
        "document_analysis": DocumentAnalysisEvaluator(),
        "relevance": RelevanceEvaluator(model_config),
    }

    print(f"  Running document analysis evaluation ({eval_data_path.name})...")
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
                    "context": "${data.context}",
                }
            }
        },
        output_path=str(Path(__file__).parent / "document_analysis_results.json"),
    )

    metrics = result.get("metrics", {})
    _print_metrics(metrics)
    return metrics


def _print_metrics(metrics: dict) -> None:
    for key, value in sorted(metrics.items()):
        if isinstance(value, float):
            print(f"    {key}: {value:.4f}")
