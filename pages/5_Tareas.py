from datetime import date

import streamlit as st
from sqlmodel import Session, select

from regrow.adapters.db.engine import engine
from regrow.adapters.db.models import (
    ClientDB,
    CompanyDB,
    ProjectDB,
    TaskDB,
    TeamMemberDB,
)
from regrow.domain.models import ProjectStatus, TaskStatus

st.set_page_config(page_title="Tareas — Regrow", layout="wide")
st.title("Tareas")

today = date.today()


def task_week(task: TaskDB, project: ProjectDB | None) -> int:
    if project is None or project.activated_at is None or task.due_date is None:
        return 0
    return max(1, (task.due_date - project.activated_at).days // 7 + 1)


def is_overdue(task: TaskDB) -> bool:
    return (
        task.due_date is not None
        and task.due_date < today
        and task.status != TaskStatus.done
    )


def days_overdue(task: TaskDB) -> int:
    if task.due_date is None:
        return 0
    return (today - task.due_date).days


def mark_done(task_id: int) -> None:
    with Session(engine) as session:
        task = session.get(TaskDB, task_id)
        if task is not None:
            task.status = TaskStatus.done
            session.commit()


with Session(engine) as session:
    members = list(session.exec(select(TeamMemberDB)).all())
    projects = list(session.exec(select(ProjectDB)).all())
    clients_by_id = {c.id: c for c in session.exec(select(ClientDB)).all()}
    companies_by_id = {c.id: c for c in session.exec(select(CompanyDB)).all()}
    all_tasks = list(session.exec(select(TaskDB)).all())

members_by_id = {m.id: m for m in members}
projects_by_id = {p.id: p for p in projects}


def project_company(project: ProjectDB) -> str:
    client = clients_by_id.get(project.client_id)
    if client is None:
        return "—"
    company = companies_by_id.get(client.company_id)
    return company.name if company else "—"


tasks_by_project: dict[int, list[TaskDB]] = {}
for t in all_tasks:
    tasks_by_project.setdefault(t.project_id, []).append(t)


# --- SECCIÓN 1 — Mis tareas ---
st.header("1. Mis tareas")

if not members:
    st.info("No hay miembros del equipo cargados.")
else:
    member_labels = {f"{m.name} ({m.role})": m for m in members}
    selected_member_label = st.selectbox(
        "Ver tareas de:", list(member_labels.keys()), key="member_select"
    )
    selected_member = member_labels[selected_member_label]
    status_filter = st.radio(
        "Filtro",
        ["Todas", "Pendientes", "Vencidas", "Completadas"],
        horizontal=True,
        key="status_filter",
    )

    member_tasks = [t for t in all_tasks if t.assigned_to == selected_member.id]

    if status_filter == "Pendientes":
        member_tasks = [t for t in member_tasks if t.status != TaskStatus.done]
    elif status_filter == "Vencidas":
        member_tasks = [t for t in member_tasks if is_overdue(t)]
    elif status_filter == "Completadas":
        member_tasks = [t for t in member_tasks if t.status == TaskStatus.done]

    if not member_tasks:
        st.caption("Sin tareas para este filtro.")
    else:
        grouped: dict[int, list[TaskDB]] = {}
        for t in member_tasks:
            grouped.setdefault(t.project_id, []).append(t)

        for pid, ptasks in grouped.items():
            project = projects_by_id.get(pid)
            project_name = project.name if project else f"Proyecto {pid}"
            company_name = project_company(project) if project else "—"
            st.subheader(f"{company_name} — {project_name}")
            for t in sorted(ptasks, key=lambda x: x.due_date or date.max):
                cols = st.columns([5, 2, 2, 2])
                if is_overdue(t):
                    cols[0].markdown(
                        f":red[⚠️ **{t.title}** — vencida hace {days_overdue(t)} días]"
                    )
                else:
                    cols[0].markdown(f"**{t.title}**")
                cols[1].markdown(f"Vence: {t.due_date or '—'}")
                cols[2].markdown(f"`{t.status}`")
                if t.status != TaskStatus.done and t.id is not None:
                    if cols[3].button("Marcar como hecha", key=f"done_mine_{t.id}"):
                        mark_done(t.id)
                        st.rerun()

st.divider()

# --- SECCIÓN 2 — Vista por proyecto ---
st.header("2. Vista por proyecto")

if not projects:
    st.info("No hay proyectos.")
else:
    project_labels = {
        f"{project_company(p)} — {p.name} (id {p.id})": p for p in projects
    }
    selected_proj_label = st.selectbox(
        "Proyecto", list(project_labels.keys()), key="proj_select"
    )
    selected_project = project_labels[selected_proj_label]
    proj_tasks = tasks_by_project.get(selected_project.id or 0, [])

    total = len(proj_tasks)
    done = sum(1 for t in proj_tasks if t.status == TaskStatus.done)
    progress = done / total if total > 0 else 0.0
    st.progress(progress, text=f"{done}/{total} completadas")

    if not proj_tasks:
        st.caption("Este proyecto no tiene tareas.")
    else:
        header_cols = st.columns([1, 5, 2, 2, 2, 2])
        headers = ["Semana", "Tarea", "Asignado", "Estado", "Vencimiento", ""]
        for col, text in zip(header_cols, headers, strict=True):
            col.markdown(f"**{text}**")

        sorted_tasks = sorted(
            proj_tasks,
            key=lambda x: (task_week(x, selected_project), x.due_date or date.max),
        )
        for t in sorted_tasks:
            row = st.columns([1, 5, 2, 2, 2, 2])
            week = task_week(t, selected_project)
            assignee = members_by_id.get(t.assigned_to or 0)
            assignee_name = assignee.name if assignee else "—"
            overdue = is_overdue(t)

            if overdue:
                row[0].markdown(f":red[{week}]")
                row[1].markdown(f":red[⚠️ {t.title}]")
                row[2].markdown(f":red[{assignee_name}]")
                row[3].markdown(f":red[`{t.status}`]")
                row[4].markdown(f":red[{t.due_date}]")
            else:
                row[0].markdown(str(week))
                row[1].markdown(t.title)
                row[2].markdown(assignee_name)
                row[3].markdown(f"`{t.status}`")
                row[4].markdown(str(t.due_date or "—"))

            if t.status != TaskStatus.done and t.id is not None:
                if row[5].button("Marcar hecha", key=f"done_proj_{t.id}"):
                    mark_done(t.id)
                    st.rerun()

st.divider()

# --- SECCIÓN 3 — ¿Quién tiene la pelota? ---
st.header("3. ¿Quién tiene la pelota?")

active_projects = [p for p in projects if p.status == ProjectStatus.active]

if not active_projects:
    st.info("No hay proyectos activos.")
else:
    for project in active_projects:
        project_tasks = tasks_by_project.get(project.id or 0, [])
        pending = [t for t in project_tasks if t.status != TaskStatus.done]
        if not pending:
            st.markdown(
                f"✅ **{project_company(project)} — {project.name}** · "
                "sin tareas pendientes"
            )
            continue

        next_task = min(
            pending,
            key=lambda x: (
                task_week(x, project),
                x.due_date or date.max,
            ),
        )
        assignee = members_by_id.get(next_task.assigned_to or 0)
        role_label = str(assignee.role) if assignee else "sin asignar"
        week_now = (
            max(1, (today - project.activated_at).days // 7 + 1)
            if project.activated_at
            else 0
        )

        if is_overdue(next_task):
            status_text = f"vencida hace {days_overdue(next_task)} días"
            icon = "🔴"
        elif next_task.due_date is not None:
            status_text = f"vence {next_task.due_date}"
            icon = "🟢"
        else:
            status_text = "sin fecha"
            icon = "🟡"

        company_name = project_company(project)
        st.markdown(
            f"{icon} **{company_name}** (semana {week_now}) → "
            f"{role_label}: {next_task.title} ({status_text})"
        )
