"""REST API routes for the ServiceDesk simulator."""

from fastapi import APIRouter, HTTPException

from database import db
from models import (
    AddCommentRequest,
    AddFeedbackRequest,
    ClosureFeedback,
    Comment,
    CreateTicketRequest,
    Ticket,
    UpdateTicketRequest,
)

router = APIRouter(prefix="/api")


@router.get("/incidents", response_model=list[Ticket])
def list_incidents(status: str | None = None, limit: int | None = None):
    """List incidents, optionally filtered by status. Supports limit for batch control."""
    tickets = db.list_all(status=status)
    if limit and limit > 0:
        tickets = tickets[:limit]
    return tickets


@router.get("/incidents/{incident_id}", response_model=Ticket)
def get_incident(incident_id: str):
    ticket = db.get(incident_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Incident not found")
    return ticket


@router.post("/incidents", response_model=Ticket, status_code=201)
def create_incident(request: CreateTicketRequest):
    return db.create(
        subject=request.subject,
        description=request.description,
        caller_name=request.caller_name,
    )


@router.patch("/incidents/{incident_id}", response_model=Ticket)
def update_incident(incident_id: str, request: UpdateTicketRequest):
    fields = request.model_dump(exclude_unset=True)
    ticket = db.update(incident_id, fields)
    if not ticket:
        raise HTTPException(status_code=404, detail="Incident not found")
    return ticket


@router.post("/incidents/{incident_id}/actions", response_model=Comment, status_code=201)
def add_action(incident_id: str, request: AddCommentRequest):
    comment = db.add_comment(
        ticket_id=incident_id,
        text=request.text,
        author=request.author,
        is_internal=request.is_internal,
    )
    if not comment:
        raise HTTPException(status_code=404, detail="Incident not found")
    return comment


@router.post("/incidents/{incident_id}/feedback", response_model=ClosureFeedback)
def add_feedback(incident_id: str, request: AddFeedbackRequest):
    feedback = db.add_feedback(
        ticket_id=incident_id,
        rating=request.rating,
        comment=request.comment,
    )
    if not feedback:
        raise HTTPException(status_code=404, detail="Incident not found")
    return feedback


@router.post("/reset")
def reset_database():
    """Reset the database to initial seed state."""
    db.reset()
    return {"message": "Database reset to initial state", "ticket_count": db.stats()["total"]}
