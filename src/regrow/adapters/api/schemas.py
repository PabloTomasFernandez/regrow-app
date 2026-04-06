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