from datetime import date

from fastapi import APIRouter, Depends, HTTPException

from regrow.adapters.api.schemas import ActivateProject, ProjectCreate
from regrow.adapters.db.engine import get_session
from regrow.adapters.db.models import ProjectDB
from regrow.adapters.db.repository import Repository
from regrow.domain.services import (
    generate_base_tasks,
    generate_checkups,
    generate_closing_tasks,
)

router = APIRouter(prefix="/projects", tags=["projects"])


def get_repo() -> Repository:
    session = get_session()
    return Repository(session)


@router.post("/")
def create_projects(project: ProjectCreate, repo: Repository = Depends(get_repo)):
    projects_db = ProjectDB(**project.model_dump())
    return repo.create_project(projects_db)


@router.post("/{project_id}/activate")
def activate_project(
    project_id: int,
    activate_project: ActivateProject,
    repo: Repository = Depends(get_repo),
):
    project = repo.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if activate_project.onboarding_date:
        onboarding_date = activate_project.onboarding_date
    else:
        onboarding_date = date.today()

    duration = project.duration_weeks
    tasks = generate_base_tasks(project_id, onboarding_date)
    tasks.extend(generate_checkups(project_id, onboarding_date, duration))
    tasks.extend(generate_closing_tasks(project_id, onboarding_date, duration))

    repo.activate_project(project_id, onboarding_date, tasks)

    return project
