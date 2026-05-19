"""In-memory database with seed/reset capability."""

from datetime import datetime, timezone

from models import Comment, ClosureFeedback, Ticket, TicketStatus
from seed_data import SEED_TICKETS


class TicketDatabase:
    """Single-responsibility in-memory ticket store."""

    def __init__(self):
        self._store: dict[str, Ticket] = {}
        self.reset()

    def reset(self) -> None:
        """Reset database to default seed state."""
        self._store.clear()
        for data in SEED_TICKETS:
            ticket = Ticket(**data)
            self._store[ticket.id] = ticket

    def list_all(self, status: str | None = None) -> list[Ticket]:
        """List tickets, optionally filtered by status."""
        tickets = list(self._store.values())
        if status:
            tickets = [t for t in tickets if t.status.value == status]
        return sorted(tickets, key=lambda t: t.created_at, reverse=True)

    def get(self, ticket_id: str) -> Ticket | None:
        return self._store.get(ticket_id)

    def create(self, subject: str, description: str, caller_name: str) -> Ticket:
        ticket = Ticket(subject=subject, description=description, caller_name=caller_name)
        self._store[ticket.id] = ticket
        return ticket

    def update(self, ticket_id: str, fields: dict) -> Ticket | None:
        ticket = self._store.get(ticket_id)
        if not ticket:
            return None
        for field, value in fields.items():
            setattr(ticket, field, value)
        ticket.updated_at = datetime.now(timezone.utc)
        return ticket

    def add_comment(self, ticket_id: str, text: str, author: str, is_internal: bool) -> Comment | None:
        ticket = self._store.get(ticket_id)
        if not ticket:
            return None
        comment = Comment(text=text, author=author, is_internal=is_internal)
        ticket.comments.append(comment)
        ticket.updated_at = datetime.now(timezone.utc)
        return comment

    def add_feedback(self, ticket_id: str, rating: int, comment: str) -> ClosureFeedback | None:
        ticket = self._store.get(ticket_id)
        if not ticket:
            return None
        feedback = ClosureFeedback(rating=rating, comment=comment)
        ticket.closure_feedback = feedback
        ticket.status = TicketStatus.CLOSED
        ticket.updated_at = datetime.now(timezone.utc)
        return feedback

    def stats(self) -> dict:
        tickets = list(self._store.values())
        return {
            "total": len(tickets),
            "open": sum(1 for t in tickets if t.status == TicketStatus.OPEN),
            "processed": sum(1 for t in tickets if t.status == TicketStatus.PROCESSED_BY_AI),
            "closed": sum(1 for t in tickets if t.status == TicketStatus.CLOSED),
        }


# Singleton instance
db = TicketDatabase()
