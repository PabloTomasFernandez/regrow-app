from datetime import date, datetime

from sqlmodel import Field, SQLModel

from regrow.domain.models import ProjectStatus, TaskStatus, TeamRole


class CompanyDB(SQLModel, table=True):
    __tablename__ = "companies"  # type: ignore[assignment]

    id: int | None = Field(default=None, primary_key=True)
    name: str
    industry: str | None = None
    linkedin_company: str | None = None
    website: str | None = None
    created_at: datetime | None = Field(default_factory=datetime.now)


class ClientDB(SQLModel, table=True):
    __tablename__ = "clients"  # type: ignore[assignment]

    id: int | None = Field(default=None, primary_key=True)
    name: str
    apellido: str
    email: str | None = None
    company_id: int = Field(foreign_key="companies.id")
    linkedin_profile: str | None = None
    ghl_profile: str | None = None
    created_at: datetime | None = Field(default_factory=datetime.now)


class TeamMemberDB(SQLModel, table=True):
    __tablename__ = "team_members"  # type: ignore[assignment]

    id: int | None = Field(default=None, primary_key=True)
    name: str
    role: TeamRole
    email: str | None = None
    is_admin: bool = False
    active: bool = True


class ProjectDB(SQLModel, table=True):
    __tablename__ = "projects"  # type: ignore[assignment]

    id: int | None = Field(default=None, primary_key=True)
    name: str
    client_id: int = Field(foreign_key="clients.id")
    status: ProjectStatus = ProjectStatus.draft
    duration_weeks: int = 14
    activated_at: date | None = None
    created_at: datetime | None = Field(default_factory=datetime.now)


class TaskDB(SQLModel, table=True):
    __tablename__ = "tasks"  # type: ignore[assignment]

    id: int | None = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="projects.id")
    title: str
    description: str | None = None
    notes: str | None = None
    status: TaskStatus = TaskStatus.pending
    assigned_to: int | None = Field(default=None, foreign_key="team_members.id")
    due_date: date | None = None
    is_auto_generated: bool = False
    campaign_id: int | None = Field(default=None, foreign_key="campaign_details.id")
    created_at: datetime | None = Field(default_factory=datetime.now)
    completed_at: date | None = None


class TaskTemplateDB(SQLModel, table=True):
    __tablename__ = "task_templates"  # type: ignore[assignment]

    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str | None = None
    role: str
    week: int
    category: str = "base"


class AssignmentDB(SQLModel, table=True):
    __tablename__ = "assignments"  # type: ignore[assignment]

    id: int | None = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="projects.id")
    member_id: int = Field(foreign_key="team_members.id")
    role: str


class CampaignDetailDB(SQLModel, table=True):
    __tablename__ = "campaign_details"  # type: ignore[assignment]

    id: int | None = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="projects.id")
    number: int
    campaign_type: str = "normal"
    industry: str = ""
    country: str = ""
    company_size: str = ""
    event_name: str | None = None
    copy_status: str = "draft"
    created_at: datetime | None = Field(default_factory=datetime.now)


class BuyerPersonaDB(SQLModel, table=True):
    __tablename__ = "buyer_personas"  # type: ignore[assignment]

    id: int | None = Field(default=None, primary_key=True)
    campaign_detail_id: int = Field(foreign_key="campaign_details.id")
    position: str
    trigger: str | None = None
    attendee_type: str | None = None
    lemlist_campaign_id: str | None = None
    status: str = "draft"
    created_at: datetime | None = Field(default_factory=datetime.now)


class SequenceDB(SQLModel, table=True):
    __tablename__ = "sequences"  # type: ignore[assignment]

    id: int | None = Field(default=None, primary_key=True)
    buyer_persona_id: int = Field(foreign_key="buyer_personas.id")
    sequence_type: str
    created_at: datetime | None = Field(default_factory=datetime.now)


class MessageDB(SQLModel, table=True):
    __tablename__ = "messages"  # type: ignore[assignment]

    id: int | None = Field(default=None, primary_key=True)
    sequence_id: int = Field(foreign_key="sequences.id")
    order: int
    subject: str | None = None
    body: str
    delay_days: int = 0
    approved: bool = False
    created_at: datetime | None = Field(default_factory=datetime.now)


class ValidationDB(SQLModel, table=True):
    __tablename__ = "validations"  # type: ignore[assignment]

    id: int | None = Field(default=None, primary_key=True)
    message_id: int = Field(foreign_key="messages.id")
    author_id: int = Field(foreign_key="team_members.id")
    text: str
    approved: bool = False
    created_at: datetime | None = Field(default_factory=datetime.now)


class CommentDB(SQLModel, table=True):
    __tablename__ = "comments"  # type: ignore[assignment]

    id: int | None = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id")
    author_id: int = Field(foreign_key="team_members.id")
    text: str
    created_at: datetime = Field(default_factory=datetime.now)
