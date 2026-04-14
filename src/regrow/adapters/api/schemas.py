from datetime import date

from pydantic import BaseModel


class CompanyCreate(BaseModel):
    name: str
    industry: str | None = None
    linkedin_company: str | None = None
    website: str | None = None


class ClientCreate(BaseModel):
    name: str
    apellido: str
    email: str | None = None
    company_id: int
    linkedin_profile: str | None = None
    ghl_profile: str | None = None


class ProjectCreate(BaseModel):
    name: str
    client_id: int
    duration_weeks: int | None = None


class ActivateProject(BaseModel):
    onboarding_date: date | None = None


class CampaignCreate(BaseModel):
    project_id: int
    number: int
    campaign_type: str = "normal"
    industry: str
    country: str
    company_size: str = ""
    event_name: str | None = None


class CopyStatusUpdate(BaseModel):
    copy_status: str


class BuyerPersonaCreate(BaseModel):
    position: str
    trigger: str | None = None
    attendee_type: str | None = None


class BuyerPersonaStatusUpdate(BaseModel):
    status: str


class LemlistIdUpdate(BaseModel):
    lemlist_campaign_id: str


class SequenceCreate(BaseModel):
    sequence_type: str


class MessageCreate(BaseModel):
    order: int
    subject: str | None = None
    body: str
    delay_days: int = 0


class ValidationCreate(BaseModel):
    author_id: int
    text: str
    approved: bool = False
