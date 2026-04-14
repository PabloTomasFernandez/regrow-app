from datetime import date

from sqlmodel import Session, select

from regrow.adapters.db.models import (
    BuyerPersonaDB,
    CampaignDetailDB,
    ClientDB,
    CompanyDB,
    MessageDB,
    ProjectDB,
    SequenceDB,
    TaskDB,
    TeamMemberDB,
    ValidationDB,
)
from regrow.domain.models import ProjectStatus, Task


class Repository:
    def __init__(self, session: Session) -> None:
        self.session = session

    # --- Companies ---

    def create_company(self, company: CompanyDB) -> CompanyDB:
        self.session.add(company)
        self.session.commit()
        self.session.refresh(company)
        return company

    def get_company(self, company_id: int) -> CompanyDB | None:
        return self.session.get(CompanyDB, company_id)

    def list_companies(self) -> list[CompanyDB]:
        return list(self.session.exec(select(CompanyDB)).all())

    # --- Clients ---

    def create_client(self, client: ClientDB) -> ClientDB:
        self.session.add(client)
        self.session.commit()
        self.session.refresh(client)
        return client

    def get_client(self, client_id: int) -> ClientDB | None:
        return self.session.get(ClientDB, client_id)

    def list_clients_by_company(self, company_id: int) -> list[ClientDB]:
        statement = select(ClientDB).where(ClientDB.company_id == company_id)
        return list(self.session.exec(statement).all())

    def list_clients(self) -> list[ClientDB]:
        return list(self.session.exec(select(ClientDB)).all())

    # --- Team Members ---

    def create_team_member(self, member: TeamMemberDB) -> TeamMemberDB:
        self.session.add(member)
        self.session.commit()
        self.session.refresh(member)
        return member

    def list_team_members(self) -> list[TeamMemberDB]:
        return list(self.session.exec(select(TeamMemberDB)).all())

    # --- Projects ---

    def create_project(self, project: ProjectDB) -> ProjectDB:
        self.session.add(project)
        self.session.commit()
        self.session.refresh(project)
        return project

    def get_project(self, project_id: int) -> ProjectDB | None:
        return self.session.get(ProjectDB, project_id)

    def activate_project(
        self, project_id: int, onboarding_date: date, tasks: list[Task]
    ) -> ProjectDB | None:
        project = self.session.get(ProjectDB, project_id)
        if project is None:
            return None

        project.status = ProjectStatus.active
        project.activated_at = onboarding_date

        for task in tasks:
            task_db = TaskDB(
                project_id=task.project_id,
                title=task.title,
                description=task.description,
                notes=task.notes,
                status=task.status,
                assigned_to=task.assigned_to,
                due_date=task.due_date,
                is_auto_generated=task.is_auto_generated,
            )
            self.session.add(task_db)

        self.session.commit()
        self.session.refresh(project)
        return project

    # --- Tasks ---

    def list_tasks_by_project(self, project_id: int) -> list[TaskDB]:
        statement = select(TaskDB).where(TaskDB.project_id == project_id)
        return list(self.session.exec(statement).all())

    def update_task_status(
        self, task_id: int, status: str, notes: str | None = None
    ) -> TaskDB | None:
        task = self.session.get(TaskDB, task_id)
        if task is None:
            return None
        task.status = status  # type: ignore[assignment]
        if notes is not None:
            task.notes = notes
        self.session.commit()
        self.session.refresh(task)
        return task

    # --- Campaigns ---

    def create_campaign(self, campaign: CampaignDetailDB) -> CampaignDetailDB:
        self.session.add(campaign)
        self.session.commit()
        self.session.refresh(campaign)
        return campaign

    def get_campaigns_by_project(self, project_id: int) -> list[CampaignDetailDB]:
        statement = select(CampaignDetailDB).where(
            CampaignDetailDB.project_id == project_id
        )
        return list(self.session.exec(statement).all())

    def get_campaign(self, campaign_id: int) -> CampaignDetailDB | None:
        return self.session.get(CampaignDetailDB, campaign_id)

    def update_campaign_copy_status(
        self, campaign_id: int, status: str
    ) -> CampaignDetailDB | None:
        campaign = self.session.get(CampaignDetailDB, campaign_id)
        if campaign is None:
            return None
        campaign.copy_status = status
        self.session.commit()
        self.session.refresh(campaign)
        return campaign

    # --- Buyer Personas ---

    def create_buyer_persona(self, bp: BuyerPersonaDB) -> BuyerPersonaDB:
        self.session.add(bp)
        self.session.commit()
        self.session.refresh(bp)
        return bp

    def get_buyer_personas_by_campaign(self, campaign_id: int) -> list[BuyerPersonaDB]:
        statement = select(BuyerPersonaDB).where(
            BuyerPersonaDB.campaign_detail_id == campaign_id
        )
        return list(self.session.exec(statement).all())

    def update_buyer_persona_status(
        self, bp_id: int, status: str
    ) -> BuyerPersonaDB | None:
        bp = self.session.get(BuyerPersonaDB, bp_id)
        if bp is None:
            return None
        bp.status = status
        self.session.commit()
        self.session.refresh(bp)
        return bp

    def set_lemlist_campaign_id(
        self, bp_id: int, lemlist_id: str
    ) -> BuyerPersonaDB | None:
        bp = self.session.get(BuyerPersonaDB, bp_id)
        if bp is None:
            return None
        bp.lemlist_campaign_id = lemlist_id
        self.session.commit()
        self.session.refresh(bp)
        return bp

    # --- Sequences & Messages ---

    def create_sequence(self, sequence: SequenceDB) -> SequenceDB:
        self.session.add(sequence)
        self.session.commit()
        self.session.refresh(sequence)
        return sequence

    def get_sequences_by_buyer_persona(self, bp_id: int) -> list[SequenceDB]:
        statement = select(SequenceDB).where(SequenceDB.buyer_persona_id == bp_id)
        return list(self.session.exec(statement).all())

    def create_message(self, message: MessageDB) -> MessageDB:
        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)
        return message

    def get_messages_by_sequence(self, sequence_id: int) -> list[MessageDB]:
        statement = select(MessageDB).where(MessageDB.sequence_id == sequence_id)
        return list(self.session.exec(statement).all())

    def approve_message(self, message_id: int) -> MessageDB | None:
        message = self.session.get(MessageDB, message_id)
        if message is None:
            return None
        message.approved = True
        self.session.commit()
        self.session.refresh(message)
        return message

    # --- Validations ---

    def create_validation(self, validation: ValidationDB) -> ValidationDB:
        self.session.add(validation)
        self.session.commit()
        self.session.refresh(validation)
        return validation

    def get_validations_by_message(self, message_id: int) -> list[ValidationDB]:
        statement = select(ValidationDB).where(ValidationDB.message_id == message_id)
        return list(self.session.exec(statement).all())
