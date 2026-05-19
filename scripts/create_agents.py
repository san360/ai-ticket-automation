"""Agent creation logic using the Foundry Agent Service (Responses API).

Creates agents via POST {project_endpoint}/agents?api-version=v1
Agents are identified by name (not GUID).
Supports idempotent deployment (deletes existing agent before recreating).
"""

import json
import requests
from pathlib import Path


def load_prompt(prompt_file: str) -> str:
    """Load agent prompt from markdown file."""
    path = Path(__file__).parent.parent / "agents" / "prompts" / prompt_file
    return path.read_text(encoding="utf-8")


def _delete_agent_if_exists(project_endpoint: str, headers: dict, agent_name: str) -> None:
    """Delete an existing agent by name (ignore if not found)."""
    resp = requests.delete(
        f"{project_endpoint}/agents/{agent_name}?api-version=v1",
        headers=headers,
    )
    if resp.status_code in (200, 204):
        print(f"  Deleted existing agent: {agent_name}")
    elif resp.status_code == 404:
        pass  # Agent doesn't exist, nothing to delete
    else:
        print(f"  Warning: delete agent returned {resp.status_code}")


def create_classifier_agent(project_endpoint: str, headers: dict, vector_store_id: str, model: str = "gpt-4.1-mini") -> str:
    """Create the classifier agent with file_search tool."""
    instructions = load_prompt("classifier-agent.md")
    agent_name = "hr-ticket-classifier"

    _delete_agent_if_exists(project_endpoint, headers, agent_name)

    payload = {
        "name": agent_name,
        "description": "Classifies HR tickets by category, subcategory, and operator group",
        "definition": {
            "kind": "prompt",
            "model": model,
            "instructions": instructions + "\n\nIMPORTANT: Always respond with valid JSON only.",
            "tools": [
                {
                    "type": "file_search",
                    "vector_store_ids": [vector_store_id],
                    "max_num_results": 20,
                }
            ],
        },
    }

    resp = requests.post(
        f"{project_endpoint}/agents?api-version=v1",
        headers=headers,
        json=payload,
    )
    resp.raise_for_status()
    result = resp.json()
    print(f"  Created Classifier Agent: {result['name']} (version {result.get('version', 'N/A')})")
    return agent_name


def create_message_agent(project_endpoint: str, headers: dict, model: str = "gpt-4.1-mini") -> str:
    """Create the message generation agent (no tools)."""
    instructions = load_prompt("message-agent.md")
    agent_name = "hr-message-generator"

    _delete_agent_if_exists(project_endpoint, headers, agent_name)

    payload = {
        "name": agent_name,
        "description": "Generates HR response messages for classified tickets",
        "definition": {
            "kind": "prompt",
            "model": model,
            "instructions": instructions + "\n\nIMPORTANT: Always respond with valid JSON only.",
            "tools": [],
        },
    }

    resp = requests.post(
        f"{project_endpoint}/agents?api-version=v1",
        headers=headers,
        json=payload,
    )
    resp.raise_for_status()
    result = resp.json()
    print(f"  Created Message Agent: {result['name']} (version {result.get('version', 'N/A')})")
    return agent_name


def create_document_analysis_agent(project_endpoint: str, headers: dict, model: str = "gpt-4.1-mini") -> str:
    """Create the document analysis agent for attachment verification."""
    instructions = load_prompt("document-analysis-agent.md")
    agent_name = "hr-document-analyzer"

    _delete_agent_if_exists(project_endpoint, headers, agent_name)

    payload = {
        "name": agent_name,
        "description": "Analyzes HR ticket attachments (medical certificates, documents) for validity and verifies doctors via web search",
        "definition": {
            "kind": "prompt",
            "model": model,
            "instructions": instructions + "\n\nIMPORTANT: Always respond with valid JSON only.",
            "tools": [
                {
                    "type": "web_search",
                    "user_location": {
                        "type": "approximate",
                        "country": "CH",
                        "city": "Zurich",
                        "region": "Zurich",
                    },
                }
            ],
        },
    }

    resp = requests.post(
        f"{project_endpoint}/agents?api-version=v1",
        headers=headers,
        json=payload,
    )
    resp.raise_for_status()
    result = resp.json()
    print(f"  Created Document Analysis Agent: {result['name']} (version {result.get('version', 'N/A')})")
    return agent_name
