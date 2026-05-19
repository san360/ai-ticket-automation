"""Upload knowledge base documents to a Foundry vector store.

Uses the new Foundry Agent Service API:
  Files:   POST {project_endpoint}/openai/v1/files
  Stores:  POST {project_endpoint}/openai/v1/vector_stores

Idempotent: reuses existing vector store if found by name.
"""

from pathlib import Path

import requests


DOCUMENTS = ["category-taxonomy.md", "sample-incidents.md", "operator-groups.md"]
VECTOR_STORE_NAME = "hr-ticket-knowledge-base"


def _find_existing_vector_store(api: str, headers: dict) -> str | None:
    """Check if a vector store with our name already exists."""
    resp = requests.get(f"{api}/vector_stores", headers=headers)
    if resp.status_code != 200:
        return None
    stores = resp.json().get("data", [])
    for store in stores:
        if store.get("name") == VECTOR_STORE_NAME:
            return store["id"]
    return None


def upload_files_to_vector_store(project_endpoint: str, headers: dict) -> str:
    """Create vector store and upload knowledge base documents. Reuses existing store if found."""
    api = f"{project_endpoint}/openai/v1"

    # Check for existing vector store
    existing_id = _find_existing_vector_store(api, headers)
    if existing_id:
        print(f"  Found existing vector store: {existing_id} (reusing)")
        return existing_id

    # Upload each document and collect file IDs
    data_dir = Path(__file__).parent.parent / "agents" / "data"
    file_ids = []
    for doc_name in DOCUMENTS:
        doc_path = data_dir / doc_name
        if not doc_path.exists():
            print(f"  WARNING: {doc_path} not found, skipping")
            continue

        file_id = _upload_file(api, headers, doc_path)
        file_ids.append(file_id)
        print(f"  Uploaded {doc_name} -> {file_id}")

    # Create vector store with all file IDs
    resp = requests.post(
        f"{api}/vector_stores",
        headers=headers,
        json={"name": VECTOR_STORE_NAME, "file_ids": file_ids},
    )
    resp.raise_for_status()
    vs_id = resp.json()["id"]
    print(f"  Created vector store: {vs_id}")

    return vs_id


def _upload_file(api: str, headers: dict, path: Path) -> str:
    """Upload a single file to Foundry."""
    with open(path, "rb") as f:
        resp = requests.post(
            f"{api}/files",
            headers={"Authorization": headers["Authorization"]},
            files={"file": (path.name, f, "text/markdown")},
            data={"purpose": "assistants"},
        )
    resp.raise_for_status()
    return resp.json()["id"]
