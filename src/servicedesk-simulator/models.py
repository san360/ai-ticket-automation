"""Domain models for the ServiceDesk simulator."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


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


class Attachment(BaseModel):
    filename: str
    content_type: str
    size_bytes: int
    extracted_text: str = ""
    url: str = ""
    analysis_result: Optional[dict] = None


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
    attachments: list[Attachment] = Field(default_factory=list)
    attachment_analysis: Optional[dict] = None
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
    attachment_analysis: Optional[dict] = None


class AddCommentRequest(BaseModel):
    text: str
    author: str = "System"
    is_internal: bool = False


class AddFeedbackRequest(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str = ""
