from datetime import date, datetime

from sqlmodel import Field, SQLModel

from regrow.domain.models import ProjectStatus, TaskStatus, TeamRole


class CompanyDB(SQLModel, table=True):
    __tablename__ = "companies"   # type: ignore[assignment]

    id: int | None = Field(default=None, primary_key=True)
    name: str
    industry: str | None = None
    linkedin_company: str | None = None
    website: str | None = None
    created_at: datetime | None = Field(default_factory=datetime.now)


class ClientDB(SQLModel, table=True):
    __tablename__ = "clients"   # type: ignore[assignment]

    id: int | None = Field(default=None, primary_key=True)
    name: str
    apellido: str
    email: str | None = None
    company_id: int = Field(foreign_key="companies.id")
    linkedin_profile: str | None = None
    ghl_profile: str | None = None
    created_at: datetime | None = Field(default_factory=datetime.now)


class TeamMemberDB(SQLModel, table=True):
    __tablename__ = "team_members"   # type: ignore[assignment]

    id: int | None = Field(default=None, primary_key=True)
    name: str
    role: TeamRole
    email: str | None = None
    is_admin: bool = False


class ProjectDB(SQLModel, table=True):
    __tablename__ = "projects"   # type: ignore[assignment]

    id: int | None = Field(default=None, primary_key=True)
    name: str
    client_id: int = Field(foreign_key="clients.id")
    status: ProjectStatus = ProjectStatus.draft
    duration_weeks: int = 14
    activated_at: date | None = None
    created_at: datetime | None = Field(default_factory=datetime.now)


class TaskDB(SQLModel, table=True):
    __tablename__ = "tasks"   # type: ignore[assignment]
 
    id: int | None = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="projects.id")
    title: str
    description: str | None = None
    notes: str | None = None
    status: TaskStatus = TaskStatus.pending
    assigned_to: int | None = Field(default=None, foreign_key="team_members.id")
    due_date: date | None = None
    is_auto_generated: bool = False
    created_at: datetime | None = Field(default_factory=datetime.now)