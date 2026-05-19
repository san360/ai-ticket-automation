"""Set up continuous evaluation for all HR agents in Azure AI Foundry.

This is a one-time setup script. Once configured, evaluations run automatically
whenever an agent produces a response (triggered by RESPONSE_COMPLETED event).

Each agent gets:
  - An evaluation group with appropriate builtin evaluators
  - A continuous evaluation rule that triggers on every response

Prerequisites:
  - Project managed identity must have "Azure AI User" role on the Foundry project
  - Agents must already be deployed

Usage:
    export FOUNDRY_ENDPOINT="https://..."
    export GPT_DEPLOYMENT="gpt-4.1-mini"
    python scripts/run_evaluation.py
"""

import os
import sys

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AzureAIDataSourceConfig,
    ContinuousEvaluationRuleAction,
    EvaluationRule,
    EvaluationRuleEventType,
    EvaluationRuleFilter,
    TestingCriterionAzureAIEvaluator,
)
from azure.identity import DefaultAzureCredential


# Agent evaluation configurations
AGENT_CONFIGS = {
    "hr-ticket-classifier": {
        "eval_name": "HR Classifier Continuous Eval",
        "rule_id": "hr-classifier-continuous-rule",
        "evaluators": [
            "builtin.intent_resolution",
            "builtin.task_adherence",
            "builtin.coherence",
            "builtin.groundedness",
        ],
    },
    "hr-message-generator": {
        "eval_name": "HR Message Generator Continuous Eval",
        "rule_id": "hr-message-continuous-rule",
        "evaluators": [
            "builtin.relevance",
            "builtin.task_adherence",
            "builtin.coherence",
            "builtin.fluency",
        ],
    },
    "hr-document-analyzer": {
        "eval_name": "HR Document Analyzer Continuous Eval",
        "rule_id": "hr-document-continuous-rule",
        "evaluators": [
            "builtin.task_adherence",
            "builtin.groundedness",
            "builtin.relevance",
        ],
    },
}


def find_existing_eval(openai_client, eval_name: str):
    """Search for an existing evaluation by name."""
    page = openai_client.evals.list(order="desc", limit=100)
    for eval_obj in page.data:
        if eval_obj.name == eval_name:
            return eval_obj
    return None


def setup_continuous_eval(project_client, openai_client, agent_name: str, config: dict, deployment_name: str):
    """Set up continuous evaluation for a single agent."""
    eval_name = config["eval_name"]
    rule_id = config["rule_id"]

    print(f"\n{'='*60}")
    print(f"Agent: {agent_name}")
    print(f"{'='*60}")

    # Check if eval already exists
    eval_obj = find_existing_eval(openai_client, eval_name)
    if eval_obj:
        print(f"  Eval already exists: {eval_obj.id}")
    else:
        # Create eval group with responses data source (for continuous eval)
        data_source_config = AzureAIDataSourceConfig(type="azure_ai_source", scenario="responses")

        testing_criteria = [
            TestingCriterionAzureAIEvaluator(
                type="azure_ai_evaluator",
                name=name.split(".")[-1],
                evaluator_name=name,
                initialization_parameters={"model": deployment_name},
                data_mapping={
                    "query": "{{item.input}}",
                    "response": "{{item.output}}",
                },
            )
            for name in config["evaluators"]
        ]

        eval_obj = openai_client.evals.create(
            name=eval_name,
            data_source_config=data_source_config,
            testing_criteria=testing_criteria,
        )
        print(f"  Created eval: {eval_obj.id}")

    # Create or update the continuous evaluation rule
    rule = project_client.evaluation_rules.create_or_update(
        id=rule_id,
        evaluation_rule=EvaluationRule(
            display_name=eval_name,
            description=f"Continuous evaluation for {agent_name} on every response",
            action=ContinuousEvaluationRuleAction(
                eval_id=eval_obj.id,
                max_hourly_runs=10,
            ),
            event_type=EvaluationRuleEventType.RESPONSE_COMPLETED,
            filter=EvaluationRuleFilter(agent_name=agent_name),
            enabled=True,
        ),
    )
    print(f"  Rule active: {rule.id} (enabled={rule.enabled})")
    print(f"  Triggers on: {agent_name} RESPONSE_COMPLETED")
    print(f"  Max hourly runs: 10")

    return eval_obj.id


def main():
    endpoint = os.environ.get("FOUNDRY_ENDPOINT")
    if not endpoint:
        print("ERROR: Set FOUNDRY_ENDPOINT environment variable.")
        sys.exit(1)

    deployment_name = os.environ.get("GPT_DEPLOYMENT", "gpt-4.1-mini")

    credential = DefaultAzureCredential()
    project_client = AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True)
    openai_client = project_client.get_openai_client()

    print("Setting up continuous evaluation for all agents...")
    print(f"Endpoint: {endpoint}")
    print(f"Judge model: {deployment_name}")

    eval_ids = {}
    for agent_name, config in AGENT_CONFIGS.items():
        eval_id = setup_continuous_eval(project_client, openai_client, agent_name, config, deployment_name)
        eval_ids[agent_name] = eval_id

    print(f"\n{'='*60}")
    print("Continuous evaluation setup complete!")
    print(f"{'='*60}")
    print("\nEval IDs:")
    for agent, eid in eval_ids.items():
        print(f"  {agent}: {eid}")
    print("\nEvaluations will now run automatically on every agent response.")
    print("View results in the Azure AI Foundry portal under Evaluations.")


if __name__ == "__main__":
    main()

