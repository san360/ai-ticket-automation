"""ServiceDesk Simulator — In-memory HR ticket system with REST API and rich UI."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

app = FastAPI(title="ServiceDesk Simulator", version="1.0.0")
templates = Jinja2Templates(directory="templates")


# --- Models ---

class TicketStatus(str, Enum):
    OPEN = "open"
    PROCESSED_BY_AI = "processed_by_ai"
    CLOSED = "closed"


class Comment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    text: str
    author: str
    is_internal: bool = False
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ClosureFeedback(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Ticket(BaseModel):
    id: str = Field(default_factory=lambda: f"INC-{str(uuid4())[:8].upper()}")
    number: str = ""
    subject: str
    description: str
    status: TicketStatus = TicketStatus.OPEN
    category: Optional[str] = None
    subcategory: Optional[str] = None
    operator_group: Optional[str] = None
    language: Optional[str] = None
    confidence: Optional[float] = None
    missing_info: list[str] = Field(default_factory=list)
    caller_name: str = "Employee"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    comments: list[Comment] = Field(default_factory=list)
    closure_feedback: Optional[ClosureFeedback] = None

    def model_post_init(self, __context):
        if not self.number:
            self.number = self.id


class CreateTicketRequest(BaseModel):
    subject: str
    description: str
    caller_name: str = "Employee"


class UpdateTicketRequest(BaseModel):
    status: Optional[TicketStatus] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    operator_group: Optional[str] = None
    language: Optional[str] = None
    confidence: Optional[float] = None
    missing_info: Optional[list[str]] = None


class AddCommentRequest(BaseModel):
    text: str
    author: str = "System"
    is_internal: bool = False


class AddFeedbackRequest(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str = ""


# --- In-Memory Database ---

db: dict[str, Ticket] = {}


def seed_database():
    """Seed with sample tickets matching the architecture document."""
    sample_tickets = [
        {
            "subject": "Krankmeldung ab Montag",
            "description": "Guten Tag, ich bin seit Montag krank und kann nicht zur Arbeit kommen. Mein Arzt hat mir ein Zeugnis ausgestellt, das ich hier anhänge. Voraussichtlich bin ich bis Freitag abwesend.",
            "caller_name": "Anna Müller",
        },
        {
            "subject": "Changement d'adresse",
            "description": "Bonjour, je viens de déménager et j'aimerais mettre à jour mon adresse. Ma nouvelle adresse est: Rue du Marché 15, 1204 Genève. Le déménagement a eu lieu le 1er mars.",
            "caller_name": "Pierre Dupont",
        },
        {
            "subject": "Lohnfrage März",
            "description": "Hi, I noticed my March payslip shows a deduction of CHF 450 under 'Other deductions' that I don't understand. Could someone explain what this is for?",
            "caller_name": "James Wilson",
        },
        {
            "subject": "Mutterschaftsurlaub planen",
            "description": "Liebe HR, ich bin schwanger und möchte meinen Mutterschaftsurlaub planen. Der errechnete Termin ist am 15. Juli. Ich möchte 2 Wochen vor dem Termin in den Urlaub gehen. Das ärztliche Attest reiche ich nächste Woche nach.",
            "caller_name": "Sarah Keller",
        },
        {
            "subject": "Signalement comportement inapproprié",
            "description": "Je souhaite signaler un comportement inapproprié de la part d'un collègue. Depuis plusieurs semaines, cette personne fait des remarques déplacées à mon égard. Je préfère ne pas donner les détails ici mais j'aimerais en parler à quelqu'un de confiance.",
            "caller_name": "Marie Leclerc",
        },
        {
            "subject": "Cambio dati bancari",
            "description": "Buongiorno, ho cambiato banca e vorrei aggiornare i miei dati bancari per il versamento dello stipendio. Il nuovo IBAN è CH93 0076 2011 6238 5295 7. La banca è UBS. Il titolare del conto sono io.",
            "caller_name": "Marco Rossi",
        },
        {
            "subject": "PRINCE2 Kurs Anfrage",
            "description": "Hallo HR-Team, ich möchte gerne an einem Projektmanagement-Kurs teilnehmen. Es handelt sich um den 'PRINCE2 Foundation' Kurs bei Digicomp vom 10.-12. April. Die Kosten betragen CHF 2'400. Mein Vorgesetzter hat mündlich zugestimmt.",
            "caller_name": "Thomas Weber",
        },
        {
            "subject": "Krank - Dauer unbekannt",
            "description": "Hallo, ich fühle mich seit gestern nicht gut und bleibe diese Woche zu Hause. Ich weiss noch nicht wann ich zurückkomme.",
            "caller_name": "Lisa Brunner",
        },
        {
            "subject": "Allocations familiales - naissance",
            "description": "Bonjour, ma femme vient d'accoucher le 5 février. Notre fils s'appelle Lucas. Je voudrais demander les allocations familiales. Ci-joint l'acte de naissance.",
            "caller_name": "Jean-Marc Favre",
        },
        {
            "subject": "Frage zum Vertrag",
            "description": "Hallo, ich habe eine Frage zu meinem Vertrag. Können Sie mich bitte zurückrufen?",
            "caller_name": "Michael Schmidt",
        },
        {
            "subject": "Reisekostenabrechnung München",
            "description": "Guten Tag, ich war letzte Woche auf Geschäftsreise in München und möchte meine Reisekosten abrechnen. Hotel: CHF 180/Nacht (2 Nächte), Zugticket: CHF 95. Die Belege sind beigefügt.",
            "caller_name": "Sandra Huber",
        },
        {
            "subject": "Work Reference Letter Request",
            "description": "Hello, I am applying for a new position externally and would need a work reference letter. Could you please prepare one in English? I have been with the company for 4 years in the Marketing department.",
            "caller_name": "David Chen",
        },
    ]

    for ticket_data in sample_tickets:
        ticket = Ticket(**ticket_data)
        db[ticket.id] = ticket


seed_database()


# --- API Endpoints (ServiceDesk API) ---

@app.get("/api/incidents", response_model=list[Ticket])
def list_incidents(status: Optional[str] = None):
    """List incidents, optionally filtered by status."""
    tickets = list(db.values())
    if status:
        tickets = [t for t in tickets if t.status.value == status]
    return sorted(tickets, key=lambda t: t.created_at, reverse=True)


@app.get("/api/incidents/{incident_id}", response_model=Ticket)
def get_incident(incident_id: str):
    """Get a single incident by ID."""
    if incident_id not in db:
        raise HTTPException(status_code=404, detail="Incident not found")
    return db[incident_id]


@app.post("/api/incidents", response_model=Ticket, status_code=201)
def create_incident(request: CreateTicketRequest):
    """Create a new incident."""
    ticket = Ticket(
        subject=request.subject,
        description=request.description,
        caller_name=request.caller_name,
    )
    db[ticket.id] = ticket
    return ticket


@app.patch("/api/incidents/{incident_id}", response_model=Ticket)
def update_incident(incident_id: str, request: UpdateTicketRequest):
    """Update an incident (classification, status, etc.)."""
    if incident_id not in db:
        raise HTTPException(status_code=404, detail="Incident not found")

    ticket = db[incident_id]
    update_data = request.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(ticket, field, value)

    ticket.updated_at = datetime.now(timezone.utc)
    db[incident_id] = ticket
    return ticket


@app.post("/api/incidents/{incident_id}/actions", response_model=Comment, status_code=201)
def add_action(incident_id: str, request: AddCommentRequest):
    """Add an action/comment to an incident."""
    if incident_id not in db:
        raise HTTPException(status_code=404, detail="Incident not found")

    comment = Comment(
        text=request.text,
        author=request.author,
        is_internal=request.is_internal,
    )
    db[incident_id].comments.append(comment)
    db[incident_id].updated_at = datetime.now(timezone.utc)
    return comment


@app.post("/api/incidents/{incident_id}/feedback", response_model=ClosureFeedback)
def add_feedback(incident_id: str, request: AddFeedbackRequest):
    """Add closure feedback to an incident."""
    if incident_id not in db:
        raise HTTPException(status_code=404, detail="Incident not found")

    feedback = ClosureFeedback(rating=request.rating, comment=request.comment)
    db[incident_id].closure_feedback = feedback
    db[incident_id].status = TicketStatus.CLOSED
    db[incident_id].updated_at = datetime.now(timezone.utc)
    return feedback


@app.post("/api/reset")
def reset_database():
    """Reset the database to initial state."""
    db.clear()
    seed_database()
    return {"message": "Database reset to initial state"}


# --- Web UI ---

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page."""
    tickets = sorted(db.values(), key=lambda t: t.created_at, reverse=True)
    stats = {
        "total": len(tickets),
        "open": sum(1 for t in tickets if t.status == TicketStatus.OPEN),
        "processed": sum(1 for t in tickets if t.status == TicketStatus.PROCESSED_BY_AI),
        "closed": sum(1 for t in tickets if t.status == TicketStatus.CLOSED),
    }
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "tickets": tickets,
        "stats": stats,
    })


@app.get("/ticket/{ticket_id}", response_class=HTMLResponse)
async def ticket_detail(request: Request, ticket_id: str):
    """Ticket detail page."""
    if ticket_id not in db:
        raise HTTPException(status_code=404, detail="Ticket not found")
    ticket = db[ticket_id]
    return templates.TemplateResponse("ticket_detail.html", {
        "request": request,
        "ticket": ticket,
    })
