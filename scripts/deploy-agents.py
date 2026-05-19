"""Deploy Foundry agents: create vector store, upload data, create agents."""

import os
import sys
from pathlib import Path

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FileSearchTool, VectorStore
from azure.identity import DefaultAzureCredential


def get_project_client() -> AIProjectClient:
    """Initialize Foundry project client."""
    endpoint = os.environ["AI_FOUNDRY_ENDPOINT"]
    project_name = os.environ["AI_PROJECT_NAME"]
    return AIProjectClient(
        endpoint=f"{endpoint}/api/projects/{project_name}",
        credential=DefaultAzureCredential(),
    )


def create_vector_store(client: AIProjectClient) -> str:
    """Create vector store and upload reference documents."""
    openai = client.get_openai_client()

    # Create vector store
    vector_store = openai.vector_stores.create(name="hr-ticket-knowledge-base")
    print(f"Created vector store: {vector_store.id}")

    # Upload documents
    data_dir = Path(__file__).parent.parent / "agents" / "data"
    documents = [
        data_dir / "category-taxonomy.md",
        data_dir / "sample-incidents.md",
        data_dir / "operator-groups.md",
    ]

    for doc_path in documents:
        if not doc_path.exists():
            print(f"WARNING: {doc_path} not found, skipping")
            continue

        with open(doc_path, "rb") as f:
            file_obj = openai.vector_stores.files.upload_and_poll(
                vector_store_id=vector_store.id,
                file=f,
            )
        print(f"Uploaded {doc_path.name} -> {file_obj.id}")

    return vector_store.id


def load_prompt(prompt_file: str) -> str:
    """Load agent prompt from file."""
    prompt_path = Path(__file__).parent.parent / "agents" / "prompts" / prompt_file
    return prompt_path.read_text(encoding="utf-8")


def create_classifier_agent(client: AIProjectClient, vector_store_id: str) -> str:
    """Create the classifier agent with file search tool."""
    openai = client.get_openai_client()
    instructions = load_prompt("classifier-agent.md")

    assistant = openai.beta.assistants.create(
        name="HR-Ticket-Classifier",
        model="gpt-4.1-mini",
        instructions=instructions,
        tools=[{"type": "file_search"}],
        tool_resources={
            "file_search": {
                "vector_store_ids": [vector_store_id]
            }
        },
    )
    print(f"Created Classifier Agent: {assistant.id}")
    return assistant.id


def create_message_agent(client: AIProjectClient) -> str:
    """Create the message agent (no tools, instructions only)."""
    openai = client.get_openai_client()
    instructions = load_prompt("message-agent.md")

    assistant = openai.beta.assistants.create(
        name="HR-Message-Generator",
        model="gpt-4.1-mini",
        instructions=instructions,
        tools=[],
    )
    print(f"Created Message Agent: {assistant.id}")
    return assistant.id


def main():
    """Main deployment entry point."""
    print("=" * 60)
    print("Deploying Foundry Agents")
    print("=" * 60)

    # Validate environment
    required_vars = ["AI_FOUNDRY_ENDPOINT", "AI_PROJECT_NAME"]
    missing = [v for v in required_vars if not os.environ.get(v)]
    if missing:
        print(f"ERROR: Missing environment variables: {', '.join(missing)}")
        sys.exit(1)

    client = get_project_client()

    # Step 1: Create vector store and upload data
    print("\n--- Step 1: Creating Vector Store ---")
    vector_store_id = create_vector_store(client)

    # Step 2: Create classifier agent
    print("\n--- Step 2: Creating Classifier Agent ---")
    classifier_id = create_classifier_agent(client, vector_store_id)

    # Step 3: Create message agent
    print("\n--- Step 3: Creating Message Agent ---")
    message_id = create_message_agent(client)

    # Output summary
    print("\n" + "=" * 60)
    print("Deployment Complete!")
    print("=" * 60)
    print(f"Vector Store ID: {vector_store_id}")
    print(f"Classifier Agent ID: {classifier_id}")
    print(f"Message Agent ID: {message_id}")
    print("\nAdd these to your Logic App configuration:")
    print(f"  VECTOR_STORE_ID={vector_store_id}")
    print(f"  CLASSIFIER_AGENT_ID={classifier_id}")
    print(f"  MESSAGE_AGENT_ID={message_id}")

    # Write outputs to file for CI consumption
    outputs_path = Path(__file__).parent / "deployment-outputs.env"
    with open(outputs_path, "w") as f:
        f.write(f"VECTOR_STORE_ID={vector_store_id}\n")
        f.write(f"CLASSIFIER_AGENT_ID={classifier_id}\n")
        f.write(f"MESSAGE_AGENT_ID={message_id}\n")
    print(f"\nOutputs saved to: {outputs_path}")


if __name__ == "__main__":
    main()
