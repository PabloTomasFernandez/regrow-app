from datetime import date

from pydantic import BaseModel

class CompanyCreate(BaseModel):
    name: str
    industry: str | None = None
    linkedin_company: str | None = None
    website: str | None = None
    
class ClientCreate (BaseModel):

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