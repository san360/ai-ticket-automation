"""Upload knowledge base documents to a Foundry vector store."""

from pathlib import Path

import requests


DOCUMENTS = ["category-taxonomy.md", "sample-incidents.md", "operator-groups.md"]


def upload_files_to_vector_store(base_url: str, headers: dict) -> str:
    """Create vector store and upload knowledge base documents."""
    api = f"{base_url}/openai"
    api_version = "api-version=2025-03-01-preview"

    # Create vector store
    resp = requests.post(
        f"{api}/vector_stores?{api_version}",
        headers=headers,
        json={"name": "hr-ticket-knowledge-base"},
    )
    resp.raise_for_status()
    vs_id = resp.json()["id"]
    print(f"  Created vector store: {vs_id}")

    # Upload each document
    data_dir = Path(__file__).parent.parent / "agents" / "data"
    for doc_name in DOCUMENTS:
        doc_path = data_dir / doc_name
        if not doc_path.exists():
            print(f"  WARNING: {doc_path} not found, skipping")
            continue

        file_id = _upload_file(api, api_version, headers, doc_path)
        _attach_to_store(api, api_version, headers, vs_id, file_id)
        print(f"  Uploaded {doc_name} -> {file_id}")

    return vs_id


def _upload_file(api: str, api_version: str, headers: dict, path: Path) -> str:
    """Upload a single file to Foundry."""
    resp = requests.post(
        f"{api}/files?{api_version}",
        headers={"Authorization": headers["Authorization"]},
        files={"file": (path.name, open(path, "rb"), "text/markdown")},
        data={"purpose": "assistants"},
    )
    resp.raise_for_status()
    return resp.json()["id"]


def _attach_to_store(api: str, api_version: str, headers: dict, vs_id: str, file_id: str) -> None:
    """Attach an uploaded file to a vector store."""
    resp = requests.post(
        f"{api}/vector_stores/{vs_id}/files?{api_version}",
        headers=headers,
        json={"file_id": file_id},
    )
    resp.raise_for_status()
