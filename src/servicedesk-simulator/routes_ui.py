"""Web UI routes for the ServiceDesk simulator."""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from database import db

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page."""
    tickets = db.list_all()
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"tickets": tickets, "stats": db.stats()},
    )


@router.get("/ticket/{ticket_id}", response_class=HTMLResponse)
async def ticket_detail(request: Request, ticket_id: str):
    """Ticket detail page."""
    ticket = db.get(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return templates.TemplateResponse(
        request=request,
        name="ticket_detail.html",
        context={"ticket": ticket},
    )
