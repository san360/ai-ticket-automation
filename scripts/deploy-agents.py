"""Deploy Foundry agents using the Agent Service (Responses API).

Creates agents via the Azure AI Foundry Agent Service REST API.
Reads agent definitions from agents/*.json for declarative configuration.
Each agent is invoked via POST /openai/v1/responses with agent_reference.
"""

import json
import os
import sys
from pathlib import Path

from azure.identity import DefaultAzureCredential

from create_agents import create_classifier_agent, create_message_agent, create_document_analysis_agent
from upload_knowledge import upload_files_to_vector_store

AGENTS_DIR = Path(__file__).parent.parent / "agents"


def get_headers() -> dict:
    """Get auth headers for AI Foundry Agent Service."""
    credential = DefaultAzureCredential()
    token = credential.get_token("https://ai.azure.com/.default")
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
    print("Deploying Foundry Agents (Agent Service - Responses API)")
    print("=" * 60)

    required_vars = ["AI_FOUNDRY_ENDPOINT"]
    missing = [v for v in required_vars if not os.environ.get(v)]
    if missing:
        print(f"ERROR: Missing environment variables: {', '.join(missing)}")
        sys.exit(1)

    project_endpoint = os.environ["AI_FOUNDRY_ENDPOINT"].rstrip("/")
    headers = get_headers()

    # Load agent definitions
    definitions = load_agent_definitions()
    model = resolve_model(definitions.get("classifier-agent", definitions[next(iter(definitions))]))
    print(f"\nProject Endpoint: {project_endpoint}")
    print(f"Model deployment: {model}")

    # Step 1: Create vector store and upload knowledge base
    print("\n--- Step 1: Creating Vector Store ---")
    vector_store_id = upload_files_to_vector_store(project_endpoint, headers)

    # Step 2: Create classifier agent
    print("\n--- Step 2: Creating Classifier Agent ---")
    classifier_name = create_classifier_agent(project_endpoint, headers, vector_store_id, model=model)

    # Step 3: Create message agent
    print("\n--- Step 3: Creating Message Agent ---")
    message_name = create_message_agent(project_endpoint, headers, model=model)

    # Step 4: Create document analysis agent
    print("\n--- Step 4: Creating Document Analysis Agent ---")
    doc_agent_name = create_document_analysis_agent(project_endpoint, headers, model=model)

    # Output summary
    print("\n" + "=" * 60)
    print("Deployment Complete!")
    print(f"  Vector Store ID:            {vector_store_id}")
    print(f"  Classifier Agent Name:      {classifier_name}")
    print(f"  Message Agent Name:         {message_name}")
    print(f"  Document Analysis Agent:    {doc_agent_name}")

    # Write outputs for CI/CD consumption
    outputs_path = Path(__file__).parent / "deployment-outputs.env"
    with open(outputs_path, "w") as f:
        f.write(f"VECTOR_STORE_ID={vector_store_id}\n")
        f.write(f"CLASSIFIER_AGENT_NAME={classifier_name}\n")
        f.write(f"MESSAGE_AGENT_NAME={message_name}\n")
        f.write(f"DOCUMENT_AGENT_NAME={doc_agent_name}\n")
    print(f"\nOutputs saved to: {outputs_path}")


if __name__ == "__main__":
    main()

