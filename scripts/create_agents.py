"""Agent creation logic using the Foundry Agent Service (Responses API).

Creates agents via POST {project_endpoint}/agents/{agent_name}/versions?api-version=v1
Agents are identified by name (not GUID).
Supports versioned deployment — each deploy creates a new version, preserving history.
Falls back to initial creation if agent doesn't exist yet.
"""

import json
import requests
from pathlib import Path


def load_prompt(prompt_file: str) -> str:
    """Load agent prompt from markdown file."""
    path = Path(__file__).parent.parent / "agents" / "prompts" / prompt_file
    return path.read_text(encoding="utf-8")


def _create_or_update_agent(project_endpoint: str, headers: dict, agent_name: str, payload: dict) -> dict:
    """Create a new version of an agent, or create the agent if it doesn't exist.

    Uses POST /agents/{name}/versions to create a new version.
    Falls back to POST /agents to create the agent initially (version 1).
    """
    # Try creating a new version (agent already exists)
    version_payload = {k: v for k, v in payload.items() if k != "name"}
    resp = requests.post(
        f"{project_endpoint}/agents/{agent_name}/versions?api-version=v1",
        headers=headers,
        json=version_payload,
    )

    if resp.status_code == 404:
        # Agent doesn't exist yet — create it (will be version 1)
        print(f"  Agent '{agent_name}' not found, creating initial version...")
        resp = requests.post(
            f"{project_endpoint}/agents?api-version=v1",
            headers=headers,
            json=payload,
        )

    resp.raise_for_status()
    return resp.json()


def create_classifier_agent(project_endpoint: str, headers: dict, vector_store_id: str, model: str = "gpt-4.1-mini") -> str:
    """Create the classifier agent with file_search tool."""
    instructions = load_prompt("classifier-agent.md")
    agent_name = "hr-ticket-classifier"

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

    result = _create_or_update_agent(project_endpoint, headers, agent_name, payload)
    print(f"  Created Classifier Agent: {result['name']} (version {result.get('version', 'N/A')})")
    return agent_name


def create_message_agent(project_endpoint: str, headers: dict, model: str = "gpt-4.1-mini") -> str:
    """Create the message generation agent (no tools)."""
    instructions = load_prompt("message-agent.md")
    agent_name = "hr-message-generator"

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

    result = _create_or_update_agent(project_endpoint, headers, agent_name, payload)
    print(f"  Created Message Agent: {result['name']} (version {result.get('version', 'N/A')})")
    return agent_name


def create_document_analysis_agent(project_endpoint: str, headers: dict, model: str = "gpt-4.1-mini") -> str:
    """Create the document analysis agent for attachment verification."""
    instructions = load_prompt("document-analysis-agent.md")
    agent_name = "hr-document-analyzer"

    payload = {
        "name": agent_name,
        "description": "Analyzes HR ticket attachments (medical certificates, invoices, receipts) for validity and verifies doctors via web search",
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

    result = _create_or_update_agent(project_endpoint, headers, agent_name, payload)
    print(f"  Created Document Analysis Agent: {result['name']} (version {result.get('version', 'N/A')})")
    return agent_name
