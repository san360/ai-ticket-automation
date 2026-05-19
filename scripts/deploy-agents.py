"""Deploy Foundry agents using the Responses API (not Assistants API).

Creates agents via the Azure AI Foundry Agent Service REST API.
Reads agent definitions from agents/*.json for declarative configuration.
Each agent is a stored configuration invoked via POST /responses with agent_id.
"""

import json
import os
import sys
from pathlib import Path

from azure.identity import DefaultAzureCredential

from create_agents import create_classifier_agent, create_message_agent
from upload_knowledge import upload_files_to_vector_store

AGENTS_DIR = Path(__file__).parent.parent / "agents"


def get_headers() -> dict:
    """Get auth headers for Cognitive Services."""
    credential = DefaultAzureCredential()
    token = credential.get_token("https://cognitiveservices.azure.com/.default")
    return {
        "Authorization": f"Bearer {token.token}",
        "Content-Type": "application/json",
    }


def load_agent_definitions() -> dict:
    """Load agent definitions from agents/*.json."""
    definitions = {}
    for def_file in AGENTS_DIR.glob("*.json"):
        with open(def_file) as f:
            agent_def = json.load(f)
        definitions[agent_def["agent_name"]] = agent_def
    return definitions


def resolve_model(definition: dict) -> str:
    """Resolve ${GPT_DEPLOYMENT} placeholder to env var."""
    model = definition["definition"]["model"]
    if model == "${GPT_DEPLOYMENT}":
        return os.environ.get("GPT_DEPLOYMENT", "gpt-4.1-mini")
    return model


def main():
    """Main deployment entry point."""
    print("=" * 60)
    print("Deploying Foundry Agents (Responses API)")
    print("=" * 60)

    required_vars = ["AI_FOUNDRY_ENDPOINT"]
    missing = [v for v in required_vars if not os.environ.get(v)]
    if missing:
        print(f"ERROR: Missing environment variables: {', '.join(missing)}")
        sys.exit(1)

    base_url = os.environ["AI_FOUNDRY_ENDPOINT"].rstrip("/")
    headers = get_headers()

    # Load agent definitions
    definitions = load_agent_definitions()
    model = resolve_model(definitions.get("classifier-agent", definitions[next(iter(definitions))]))
    print(f"\nModel deployment: {model}")

    # Step 1: Create vector store and upload knowledge base
    print("\n--- Step 1: Creating Vector Store ---")
    vector_store_id = upload_files_to_vector_store(base_url, headers)

    # Step 2: Create classifier agent
    print("\n--- Step 2: Creating Classifier Agent ---")
    classifier_id = create_classifier_agent(base_url, headers, vector_store_id, model=model)

    # Step 3: Create message agent
    print("\n--- Step 3: Creating Message Agent ---")
    message_id = create_message_agent(base_url, headers, model=model)

    # Output summary
    print("\n" + "=" * 60)
    print("Deployment Complete!")
    print(f"  Vector Store ID:      {vector_store_id}")
    print(f"  Classifier Agent ID:  {classifier_id}")
    print(f"  Message Agent ID:     {message_id}")

    # Write outputs for CI/CD consumption
    outputs_path = Path(__file__).parent / "deployment-outputs.env"
    with open(outputs_path, "w") as f:
        f.write(f"VECTOR_STORE_ID={vector_store_id}\n")
        f.write(f"CLASSIFIER_AGENT_ID={classifier_id}\n")
        f.write(f"MESSAGE_AGENT_ID={message_id}\n")
    print(f"\nOutputs saved to: {outputs_path}")


if __name__ == "__main__":
    main()

