# Option D: Logic Apps (Parent–Child) + Foundry Agents — Responses API

## Overview

A Logic Apps Standard (WS1) deployment in Switzerland North orchestrates the end-to-end processing of HR tickets from TOPdesk. It uses a **parent–child workflow pattern** where the parent handles scheduling and iteration, and the child handles per-ticket AI classification and messaging via Microsoft Foundry Agents (Responses API).

**Key design decisions:**

- No agent loops — single synchronous POST per agent call
- No Table Storage / watermark — TOPdesk `status` column is the state machine (`open` → `processed`)
- No Dead Letter Queue — child workflow failures are visible in Logic Apps run history; retry via built-in retry policies
- All Logic Apps actions are GA (Generally Available)

---

## Components

| Component | Service | Region |
|-----------|---------|--------|
| Orchestrator | Logic Apps Standard (WS1) | Switzerland North |
| Classifier-Agent | Microsoft Foundry Agent Service | — |
| Message-Agent | Microsoft Foundry Agent Service | — |
| Ticket System | TOPdesk SaaS (Incident API v4.2.4) | External |
| Secrets | Azure Key Vault | Switzerland North |
| Knowledge Base | Foundry Vector Store (auto-chunked & embedded) | — |

---

## Parent Workflow — Scheduler & Iterator

The parent workflow is responsible for polling TOPdesk and dispatching work to the child.

```
⏱ Recurrence (Scheduled)
    → HTTP GET: Poll TOPdesk (filter: status == "open")
        → For Each Ticket
            → Call Child Workflow (pass ticket payload)
```

### Steps

| # | Action | Details |
|---|--------|---------|
| 1 | **Recurrence trigger** | Scheduled interval (configurable) |
| 2 | **HTTP GET** | `GET /incidents?status=open` — FIQL query against TOPdesk API v4.2.4. No watermark needed; the status column itself acts as the state machine. |
| 3 | **For Each** | Iterates over returned open tickets |
| 4 | **Call workflow in this logic app** (GA action) | Passes the full ticket payload to the child workflow |

---

## Child Workflow — Per-Ticket Processing

The child workflow processes a single ticket: classifies it, generates a message, and writes results back to TOPdesk.

```
Request Trigger (from Parent)
    → HTTP POST: Foundry Classifier-Agent (Responses API)
        → Parse JSON (Classification)
            → HTTP POST: Foundry Message-Agent (Responses API)
                → Parse JSON (Message)
                    → HTTP PATCH: Write Classification to TOPdesk
                        → HTTP POST: Post Action Note to TOPdesk
                            → Response (200 OK)
```

### Steps

| # | Action | Details |
|---|--------|---------|
| 1 | **Request trigger** | Receives ticket payload from parent workflow |
| 2 | **HTTP POST — Classifier-Agent** | Single `POST /responses` to Foundry. Synchronous response — no thread/run/poll loop. |
| 3 | **Parse JSON** | Extracts classification fields from Classifier-Agent response |
| 4 | **HTTP POST — Message-Agent** | Single `POST /responses` to Foundry. Passes classification result + original ticket. Synchronous. |
| 5 | **Parse JSON** | Extracts message fields from Message-Agent response |
| 6 | **HTTP PATCH** | Writes classification (category, subcategory, operator group) to TOPdesk incident |
| 7 | **HTTP POST** | Posts the action note (HR summary + employee message) to the TOPdesk incident |
| 8 | **Response** | Returns 200 OK to parent workflow |

---

## Classifier-Agent (gpt-4.1-mini)

### Responsibilities

- Assigns **category & subcategory** from taxonomy
- Identifies correct **operator group**
- Detects **ticket language** (DE / FR / IT / EN)
- Flags any **missing required information**\*

> \*Missing info = requirements per category. For example, to process a sick leave, a doctor's certificate must be added. A list of requirements per category is provided in the Vector Store context and the LLM validates against that.

### Tool

**File Search** — retrieves context from the Foundry Vector Store containing three documents:

| Document | Purpose |
|----------|---------|
| Sample Incidents | Few-shot examples for accurate classification |
| Category Taxonomy | Full list of categories, subcategories, and their definitions |
| Operator Group IDs | Mapping of operator groups to their TOPdesk identifiers |

### Output JSON

```json
{
  "category": "string",
  "subcategory": "string",
  "operatorGroup": "string",
  "language": "DE | FR | IT | EN",
  "missingInfo": ["string"]
}
```

---

## Message-Agent (gpt-4.1-mini)

### Responsibilities

- Generates **HR summary in English** (for the HR specialist)
- Generates **employee message** in ticket language + English
- **Scenario A**: confirms ticket is being processed (when all info is present)
- **Scenario B**: requests specific missing field from employee (when `missingInfo[]` is non-empty)

### Tool

None — **instructions-only** (no file search, no tools). All behaviour is driven by the system prompt and the classification result passed as input.

### Output JSON

```json
{
  "hrSummary": "string",
  "employeeMessage": "string",
  "scenario": "A | B"
}
```

---

## TOPdesk Integration

| Operation | Method | Endpoint | Purpose |
|-----------|--------|----------|---------|
| Poll open tickets | `GET` | `/incidents?status=open` | Parent workflow fetches unprocessed tickets |
| Write classification | `PATCH` | `/incidents/{id}` | Child writes category, subcategory, operator group |
| Post action note | `POST` | `/incidents/{id}/actions` | Child posts HR summary + employee message |

The TOPdesk **status column** serves as the state machine:
- `open` → ticket awaiting processing
- `processed` → ticket has been classified and messaged

No separate watermark or Table Storage is needed.

---

## Vector Store (Foundry)

Documents are uploaded to a Foundry Vector Store, auto-chunked and embedded. Used **only** by the Classifier-Agent via File Search.

| Document | Content |
|----------|---------|
| Sample Incidents | Reference incidents with correct classifications (few-shot) |
| Category Taxonomy | Hierarchical category → subcategory definitions |
| Operator Group IDs | Group names mapped to TOPdesk IDs |

---

## Security

| Concern | Solution |
|---------|----------|
| TOPdesk API credentials | Stored in Azure Key Vault |
| Foundry API key | Stored in Azure Key Vault |
| Access to Key Vault | Logic App managed identity |

---

## Error Handling

| Concern | Solution |
|---------|----------|
| Child workflow failure | Visible in Logic Apps **run history** |
| Transient errors | Logic Apps **built-in retry policies** (exponential backoff) |
| Dead letters | Not needed — failed runs are retained and can be resubmitted from the portal |

---

## Architecture Badges

| Property | Status |
|----------|--------|
| Logic Apps actions | All GA ✅ |
| Agent loop | None — single POST per agent |
| API style | Responses API (synchronous) |
| State management | No Table Storage — TOPdesk status column |
| Pattern | Parent–Child workflow |
| DLQ | Not required |
