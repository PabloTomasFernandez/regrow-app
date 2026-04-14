from fastapi import APIRouter, Depends, HTTPException

from regrow.adapters.api.schemas import CompanyCreate
from regrow.adapters.db.engine import get_session
from regrow.adapters.db.models import CompanyDB
from regrow.adapters.db.repository import Repository

router = APIRouter(prefix="/companies", tags=["companies"])


def get_repo() -> Repository:
    session = get_session()
    return Repository(session)


@router.get("/")
def list_companies(repo: Repository = Depends(get_repo)):
    return repo.list_companies()


@router.post("/")
def create_company(company: CompanyCreate, repo: Repository = Depends(get_repo)):
    company_db = CompanyDB(**company.model_dump())
    return repo.create_company(company_db)


@router.get("/{company_id}")
def get_company(company_id: int, repo: Repository = Depends(get_repo)):
    company = repo.get_company(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company
