"""Agent creation logic using the Responses API stored agents."""

import json
import requests
from pathlib import Path


def load_prompt(prompt_file: str) -> str:
    """Load agent prompt from markdown file."""
    path = Path(__file__).parent.parent / "agents" / "prompts" / prompt_file
    return path.read_text(encoding="utf-8")


def create_classifier_agent(base_url: str, headers: dict, vector_store_id: str, model: str = "gpt-4.1-mini") -> str:
    """Create the classifier agent with file_search tool."""
    instructions = load_prompt("classifier-agent.md")

    payload = {
        "model": model,
        "name": "HR-Ticket-Classifier",
        "instructions": instructions,
        "tools": [
            {
                "type": "file_search",
                "vector_store_ids": [vector_store_id]
            }
        ],
        "response_format": {"type": "json_object"},
    }

    resp = requests.post(
        f"{base_url}/openai/agents?api-version=2025-03-01-preview",
        headers=headers,
        json=payload,
    )
    resp.raise_for_status()
    agent_id = resp.json()["id"]
    print(f"  Created Classifier Agent: {agent_id}")
    return agent_id


def create_message_agent(base_url: str, headers: dict, model: str = "gpt-4.1-mini") -> str:
    """Create the message generation agent (no tools)."""
    instructions = load_prompt("message-agent.md")

    payload = {
        "model": model,
        "name": "HR-Message-Generator",
        "instructions": instructions,
        "tools": [],
        "response_format": {"type": "json_object"},
    }

    resp = requests.post(
        f"{base_url}/openai/agents?api-version=2025-03-01-preview",
        headers=headers,
        json=payload,
    )
    resp.raise_for_status()
    agent_id = resp.json()["id"]
    print(f"  Created Message Agent: {agent_id}")
    return agent_id
