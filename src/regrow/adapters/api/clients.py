from fastapi import APIRouter, Depends, HTTPException
from regrow.adapters.api.schemas import ClientCreate
from regrow.adapters.db.models import ClientDB
from regrow.adapters.db.repository import Repository
from regrow.adapters.db.engine import get_session

router = APIRouter(prefix="/clients", tags=["clients"])

def get_repo() -> Repository:
    session = get_session()
    return Repository(session)

@router.get("/")
def list_clients(repo: Repository = Depends(get_repo)):
    return repo.list_clients()

@router.get("/by-company/{company_id}")
def get_clients_by_company(company_id: int, repo: Repository = Depends(get_repo)):
    clients = repo.list_clients_by_company(company_id)
    return clients

@router.get("/{client_id}")
def get_clients(client_id: int, repo: Repository = Depends(get_repo)):
    client = repo.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.post("/")
def create_client(client: ClientCreate, repo: Repository = Depends(get_repo)):
    client_db = ClientDB(**client.model_dump())
    return repo.create_client(client_db)

