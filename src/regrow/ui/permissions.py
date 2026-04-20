import streamlit as st
from sqlmodel import Session, select

from regrow.adapters.db.engine import engine
from regrow.adapters.db.models import AssignmentDB, ProjectDB, TeamMemberDB
from regrow.ui.viewer import current_viewer


def is_admin(member: TeamMemberDB | None) -> bool:
    return member is not None and member.is_admin


def require_admin() -> None:
    member = current_viewer()
    if not is_admin(member):
        st.warning("⚠️ Solo administradores pueden acceder a esta página.")
        st.stop()


def _assigned_project_ids(member_id: int) -> set[int]:
    with Session(engine) as session:
        assignments = list(
            session.exec(
                select(AssignmentDB).where(AssignmentDB.member_id == member_id)
            ).all()
        )
    return {a.project_id for a in assignments}


def can_see_project(member: TeamMemberDB | None, project_id: int) -> bool:
    if member is None:
        return False
    if member.is_admin:
        return True
    if member.id is None:
        return False
    return project_id in _assigned_project_ids(member.id)


def filter_visible_projects(
    member: TeamMemberDB | None, projects: list[ProjectDB]
) -> list[ProjectDB]:
    if member is None:
        return []
    if member.is_admin:
        return projects
    if member.id is None:
        return []
    pids = _assigned_project_ids(member.id)
    return [p for p in projects if p.id in pids]


def viewer_roles_in_project(member: TeamMemberDB | None, project_id: int) -> set[str]:
    if member is None or member.id is None:
        return set()
    with Session(engine) as session:
        rows = list(
            session.exec(
                select(AssignmentDB)
                .where(AssignmentDB.member_id == member.id)
                .where(AssignmentDB.project_id == project_id)
            ).all()
        )
    return {a.role for a in rows}
