from pydantic import BaseModel

class CompanyCreate(BaseModel):
    name: str
    industry: str | None = None
    linkedin_company: str | None = None
    website: str | None = None
    