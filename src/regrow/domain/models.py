from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel


class ProjectStatus(StrEnum):
    draft = "draft"
    onboarding = "onboarding"
    active = "active"
    paused = "paused"
    completed = "completed"


class TaskStatus(StrEnum):
    pending = "pending"
    in_progress = "in_progress"
    done = "done"


class TeamRole(StrEnum):
    sdr = "sdr"
    copy = "copy"
    account_manager = "account_manager"
    coo = "coo"
    pusher = "pusher"
    automater = "automater"


class CopyStatus(StrEnum):
    draft = "draft"
    in_review = "in_review"
    validated = "validated"


class CampaignType(StrEnum):
    normal = "normal"
    event = "event"


class SequenceType(StrEnum):
    linkedin = "linkedin"
    email_connected = "email_connected"
    email_cold = "email_cold"


class AttendeeType(StrEnum):
    sponsor = "sponsor"
    attendee = "attendee"


class Company(BaseModel):
    id: int | None = None
    name: str
    industry: str | None = None
    created_at: datetime | None = None
    linkedin_company: str | None = None
    website: str | None = None


class Client(BaseModel):
    id: int | None = None
    name: str
    apellido: str
    email: str | None = None
    company_id: int
    created_at: datetime | None = None
    linkedin_profile: str | None = None
    ghl_profile: str | None = None


class TeamMember(BaseModel):
    id: int | None = None
    name: str
    role: TeamRole
    email: str | None = None
    is_admin: bool = False


class Project(BaseModel):
    id: int | None = None
    name: str
    client_id: int
    status: ProjectStatus = ProjectStatus.draft
    activated_at: date | None = None
    created_at: datetime | None = None


class Task(BaseModel):
    id: int | None = None
    project_id: int
    title: str
    description: str | None = None
    notes: str | None = None  # nuevo
    status: TaskStatus = TaskStatus.pending
    assigned_to: int | None = None
    due_date: date | None = None
    is_auto_generated: bool = False
    created_at: datetime | None = None


class CampaignDetail(BaseModel):
    id: int | None = None
    project_id: int
    number: int
    campaign_type: CampaignType
    industry: str
    country: str
    company_size: str
    event_name: str | None = None
    copy_status: CopyStatus = CopyStatus.draft
    created_at: datetime | None = None


class BuyerPersona(BaseModel):
    id: int | None = None
    campaign_detail_id: int
    position: str
    trigger: str | None = None
    attendee_type: AttendeeType | None = None
    lemlist_campaign_id: str | None = None
    status: CopyStatus = CopyStatus.draft
    created_at: datetime | None = None


class Sequence(BaseModel):
    id: int | None = None
    buyer_persona_id: int
    sequence_type: SequenceType
    created_at: datetime | None = None


class Message(BaseModel):
    id: int | None = None
    sequence_id: int
    order: int
    subject: str | None = None
    body: str
    delay_days: int = 0
    approved: bool = False
    created_at: datetime | None = None


class Validation(BaseModel):
    id: int | None = None
    message_id: int
    author_id: int
    text: str
    approved: bool = False
    created_at: datetime | None = None
