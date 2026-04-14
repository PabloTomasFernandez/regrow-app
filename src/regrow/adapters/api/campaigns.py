from fastapi import APIRouter, Depends, HTTPException

from regrow.adapters.api.schemas import (
    BuyerPersonaCreate,
    BuyerPersonaStatusUpdate,
    CampaignCreate,
    CopyStatusUpdate,
    LemlistIdUpdate,
    MessageCreate,
    SequenceCreate,
    ValidationCreate,
)
from regrow.adapters.db.engine import get_session
from regrow.adapters.db.models import (
    BuyerPersonaDB,
    CampaignDetailDB,
    MessageDB,
    SequenceDB,
    ValidationDB,
)
from regrow.adapters.db.repository import Repository

router = APIRouter(tags=["campaigns"])


def get_repo() -> Repository:
    session = get_session()
    return Repository(session)


# --- Campaigns ---


@router.post("/campaigns/")
def create_campaign(campaign: CampaignCreate, repo: Repository = Depends(get_repo)):
    campaign_db = CampaignDetailDB(**campaign.model_dump())
    return repo.create_campaign(campaign_db)


@router.get("/campaigns/by-project/{project_id}")
def list_campaigns_by_project(project_id: int, repo: Repository = Depends(get_repo)):
    return repo.get_campaigns_by_project(project_id)


@router.get("/campaigns/{campaign_id}")
def get_campaign(campaign_id: int, repo: Repository = Depends(get_repo)):
    campaign = repo.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.patch("/campaigns/{campaign_id}/copy-status")
def update_campaign_copy_status(
    campaign_id: int,
    payload: CopyStatusUpdate,
    repo: Repository = Depends(get_repo),
):
    campaign = repo.update_campaign_copy_status(campaign_id, payload.copy_status)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


# --- Buyer Personas ---


@router.post("/campaigns/{campaign_id}/buyer-personas")
def create_buyer_persona(
    campaign_id: int,
    buyer_persona: BuyerPersonaCreate,
    repo: Repository = Depends(get_repo),
):
    if not repo.get_campaign(campaign_id):
        raise HTTPException(status_code=404, detail="Campaign not found")
    bp_db = BuyerPersonaDB(campaign_detail_id=campaign_id, **buyer_persona.model_dump())
    return repo.create_buyer_persona(bp_db)


@router.get("/campaigns/{campaign_id}/buyer-personas")
def list_buyer_personas(campaign_id: int, repo: Repository = Depends(get_repo)):
    return repo.get_buyer_personas_by_campaign(campaign_id)


@router.patch("/buyer-personas/{bp_id}/status")
def update_buyer_persona_status(
    bp_id: int,
    payload: BuyerPersonaStatusUpdate,
    repo: Repository = Depends(get_repo),
):
    bp = repo.update_buyer_persona_status(bp_id, payload.status)
    if not bp:
        raise HTTPException(status_code=404, detail="Buyer persona not found")
    return bp


@router.patch("/buyer-personas/{bp_id}/lemlist-id")
def set_lemlist_campaign_id(
    bp_id: int,
    payload: LemlistIdUpdate,
    repo: Repository = Depends(get_repo),
):
    bp = repo.set_lemlist_campaign_id(bp_id, payload.lemlist_campaign_id)
    if not bp:
        raise HTTPException(status_code=404, detail="Buyer persona not found")
    return bp


# --- Sequences ---


@router.post("/buyer-personas/{bp_id}/sequences")
def create_sequence(
    bp_id: int,
    sequence: SequenceCreate,
    repo: Repository = Depends(get_repo),
):
    sequence_db = SequenceDB(buyer_persona_id=bp_id, **sequence.model_dump())
    return repo.create_sequence(sequence_db)


@router.get("/buyer-personas/{bp_id}/sequences")
def list_sequences(bp_id: int, repo: Repository = Depends(get_repo)):
    return repo.get_sequences_by_buyer_persona(bp_id)


# --- Messages ---


@router.post("/sequences/{sequence_id}/messages")
def create_message(
    sequence_id: int,
    message: MessageCreate,
    repo: Repository = Depends(get_repo),
):
    message_db = MessageDB(sequence_id=sequence_id, **message.model_dump())
    return repo.create_message(message_db)


@router.get("/sequences/{sequence_id}/messages")
def list_messages(sequence_id: int, repo: Repository = Depends(get_repo)):
    return repo.get_messages_by_sequence(sequence_id)


@router.patch("/messages/{message_id}/approve")
def approve_message(message_id: int, repo: Repository = Depends(get_repo)):
    message = repo.approve_message(message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message


# --- Validations ---


@router.post("/messages/{message_id}/validations")
def create_validation(
    message_id: int,
    validation: ValidationCreate,
    repo: Repository = Depends(get_repo),
):
    validation_db = ValidationDB(message_id=message_id, **validation.model_dump())
    return repo.create_validation(validation_db)


@router.get("/messages/{message_id}/validations")
def list_validations(message_id: int, repo: Repository = Depends(get_repo)):
    return repo.get_validations_by_message(message_id)
