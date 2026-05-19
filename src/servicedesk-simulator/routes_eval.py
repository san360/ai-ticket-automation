"""Evaluation API routes for continuous per-run metrics tracking."""

from fastapi import APIRouter, HTTPException

from database import db
from models import EvaluationRun, RecordEvaluationRequest

router = APIRouter(prefix="/api/evaluations")

# In-memory evaluation store
_eval_store: list[EvaluationRun] = []

# Quality gates for continuous evaluation
CONTINUOUS_GATES = {
    "min_confidence": 0.60,
    "document_verification_required": True,
}


def _check_quality_gates(run: EvaluationRun) -> tuple[bool, list[str]]:
    """Check quality gates against a single evaluation run."""
    failures = []
    m = run.metrics

    # Confidence gate
    if m.classification_confidence is not None and m.classification_confidence < CONTINUOUS_GATES["min_confidence"]:
        failures.append(f"classification_confidence {m.classification_confidence:.2f} < {CONTINUOUS_GATES['min_confidence']}")

    # Document verification gate
    if m.document_analysis_performed and CONTINUOUS_GATES["document_verification_required"]:
        if m.doctor_verified == "not_found":
            failures.append("doctor_verified=not_found (potential fraud)")

    return len(failures) == 0, failures


@router.post("", response_model=EvaluationRun, status_code=201)
def record_evaluation(request: RecordEvaluationRequest):
    """Record evaluation metrics for a ticket processing run."""
    ticket = db.get(request.ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    run = EvaluationRun(
        ticket_id=request.ticket_id,
        ticket_subject=ticket.subject,
        metrics=request.metrics,
        agent_outputs=request.agent_outputs,
    )

    passed, failures = _check_quality_gates(run)
    run.passed_quality_gates = passed
    run.gate_failures = failures

    _eval_store.append(run)
    return run


@router.get("", response_model=list[EvaluationRun])
def list_evaluations(limit: int = 50):
    """List recent evaluation runs."""
    return sorted(_eval_store, key=lambda r: r.run_timestamp, reverse=True)[:limit]


@router.get("/summary")
def evaluation_summary():
    """Get aggregated evaluation summary."""
    if not _eval_store:
        return {
            "total_runs": 0,
            "passed": 0,
            "failed": 0,
            "pass_rate": 0.0,
            "avg_confidence": 0.0,
            "document_analysis_count": 0,
            "doctor_verification_stats": {"verified": 0, "not_found": 0, "inconclusive": 0},
            "common_failures": [],
        }

    total = len(_eval_store)
    passed = sum(1 for r in _eval_store if r.passed_quality_gates)
    confidences = [r.metrics.classification_confidence for r in _eval_store if r.metrics.classification_confidence is not None]
    doc_runs = [r for r in _eval_store if r.metrics.document_analysis_performed]

    verification_stats = {"verified": 0, "not_found": 0, "inconclusive": 0}
    for r in doc_runs:
        v = r.metrics.doctor_verified
        if v in verification_stats:
            verification_stats[v] += 1

    # Aggregate failure reasons
    failure_counts: dict[str, int] = {}
    for r in _eval_store:
        for f in r.gate_failures:
            failure_counts[f] = failure_counts.get(f, 0) + 1
    common_failures = sorted(failure_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "total_runs": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": passed / total if total > 0 else 0.0,
        "avg_confidence": sum(confidences) / len(confidences) if confidences else 0.0,
        "document_analysis_count": len(doc_runs),
        "doctor_verification_stats": verification_stats,
        "common_failures": [{"reason": r, "count": c} for r, c in common_failures],
    }


@router.get("/{eval_id}", response_model=EvaluationRun)
def get_evaluation(eval_id: str):
    """Get a specific evaluation run."""
    for run in _eval_store:
        if run.id == eval_id:
            return run
    raise HTTPException(status_code=404, detail="Evaluation run not found")


@router.post("/reset")
def reset_evaluations():
    """Clear all evaluation data."""
    _eval_store.clear()
    return {"message": "Evaluation store cleared"}
