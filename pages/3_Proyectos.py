from datetime import date

import streamlit as st
from sqlmodel import Session, select

from regrow.adapters.db.engine import engine
from regrow.adapters.db.models import (
    AssignmentDB,
    ClientDB,
    CompanyDB,
    ProjectDB,
    TaskDB,
    TeamMemberDB,
)
from regrow.domain.models import ProjectStatus, TeamRole
from regrow.domain.services import (
    generate_base_tasks,
    generate_checkups,
    generate_closing_tasks,
)

st.set_page_config(page_title="Proyectos — Regrow", layout="wide")
st.title("Proyectos")


def current_week(activated_at: date | None, today: date) -> int:
    if activated_at is None:
        return 0
    return max(1, (today - activated_at).days // 7 + 1)


with Session(engine) as session:
    clients = list(session.exec(select(ClientDB)).all())
    companies_by_id = {c.id: c for c in session.exec(select(CompanyDB)).all()}
    all_members = list(session.exec(select(TeamMemberDB)).all())

if not clients:
    st.warning("Primero tenés que crear al menos un cliente.")
    st.stop()

members_by_role: dict[str, list[TeamMemberDB]] = {}
for m in all_members:
    members_by_role.setdefault(m.role, []).append(m)


def client_label(client: ClientDB) -> str:
    company = companies_by_id.get(client.company_id)
    company_name = company.name if company else "—"
    return f"{client.name} {client.apellido} · {company_name} (id {client.id})"


def member_label(member: TeamMemberDB) -> str:
    return f"{member.name} (id {member.id})"


ASSIGNMENT_ROLES = [
    ("Account Manager", TeamRole.account_manager),
    ("SDR", TeamRole.sdr),
    ("Copy", TeamRole.copy),
    ("Pusher", TeamRole.pusher),
    ("Automater", TeamRole.automater),
]

client_by_label = {client_label(c): c for c in clients}

with st.form("create_project", clear_on_submit=True):
    st.subheader("Crear proyecto")
    label = st.selectbox("Cliente *", list(client_by_label.keys()))
    name = st.text_input("Nombre del proyecto *")
    duration_weeks = st.number_input(
        "Duración (semanas)", min_value=1, max_value=52, value=14, step=1
    )

    st.markdown("**Equipo del proyecto**")
    role_selections: dict[str, str] = {}
    for display_name, role_enum in ASSIGNMENT_ROLES:
        candidates = members_by_role.get(role_enum, [])
        if not candidates:
            candidates = all_members
        options = [member_label(m) for m in candidates]
        role_selections[role_enum] = st.selectbox(
            display_name, options, key=f"role_{role_enum}"
        )

    submitted = st.form_submit_button("Crear proyecto")

    if submitted:
        if not name.strip():
            st.error("El nombre es obligatorio.")
        else:
            client = client_by_label[label]
            if client.id is None:
                st.error("El cliente seleccionado no tiene ID.")
            else:
                with Session(engine) as session:
                    project = ProjectDB(
                        name=name.strip(),
                        client_id=client.id,
                        duration_weeks=int(duration_weeks),
                    )
                    session.add(project)
                    session.commit()
                    session.refresh(project)
                    assert project.id is not None

                    for role_val, sel_label in role_selections.items():
                        mid_str = sel_label.split("id ")[-1].rstrip(")")
                        session.add(
                            AssignmentDB(
                                project_id=project.id,
                                member_id=int(mid_str),
                                role=role_val,
                            )
                        )
                    session.commit()
                st.success(f"Proyecto '{name}' creado con equipo asignado.")
                st.rerun()

st.subheader("Listado de proyectos")

with Session(engine) as session:
    projects = list(session.exec(select(ProjectDB)).all())
    clients_by_id = {c.id: c for c in session.exec(select(ClientDB)).all()}
    tasks_by_project: dict[int, int] = {}
    for task in session.exec(select(TaskDB)).all():
        tasks_by_project[task.project_id] = tasks_by_project.get(task.project_id, 0) + 1
    all_assignments = list(session.exec(select(AssignmentDB)).all())

assignments_by_project: dict[int, list[AssignmentDB]] = {}
for a in all_assignments:
    assignments_by_project.setdefault(a.project_id, []).append(a)

members_by_id = {m.id: m for m in all_members}

if not projects:
    st.info("Todavía no hay proyectos cargados.")

today = date.today()

for project in projects:
    client = clients_by_id.get(project.client_id)
    company_name = "—"
    if client is not None:
        company = companies_by_id.get(client.company_id)
        if company is not None:
            company_name = company.name

    title = f"{project.name} — {company_name} · `{project.status}`"
    with st.expander(title):
        st.markdown(
            f"**ID:** {project.id}  \n"
            f"**Duración:** {project.duration_weeks} semanas  \n"
            f"**Activado:** {project.activated_at or '—'}"
        )

        proj_assignments = assignments_by_project.get(project.id or 0, [])
        if proj_assignments:
            team_lines: list[str] = []
            for a in proj_assignments:
                m = members_by_id.get(a.member_id)
                m_name = m.name if m else f"ID {a.member_id}"
                team_lines.append(f"- **{a.role}**: {m_name}")
            st.markdown("**Equipo:**  \n" + "  \n".join(team_lines))

        def change_status(pid: int | None, new_status: ProjectStatus) -> None:
            if pid is None:
                st.error("El proyecto no tiene ID.")
                return
            with Session(engine) as s:
                db_proj = s.get(ProjectDB, pid)
                if db_proj is None:
                    st.error("Proyecto no encontrado.")
                    return
                db_proj.status = new_status
                s.commit()

        if project.status == ProjectStatus.active:
            week = current_week(project.activated_at, today)
            task_count = tasks_by_project.get(project.id or 0, 0)
            st.metric("Semana actual", f"{week}/{project.duration_weeks}")
            st.metric("Tareas", task_count)
            btn_cols = st.columns(2)
            if btn_cols[0].button("Pausar proyecto", key=f"pause_{project.id}"):
                change_status(project.id, ProjectStatus.paused)
                st.rerun()
            if btn_cols[1].button("Completar proyecto", key=f"complete_{project.id}"):
                change_status(project.id, ProjectStatus.completed)
                st.rerun()
        elif project.status == ProjectStatus.paused:
            if st.button("Reactivar proyecto", key=f"resume_{project.id}"):
                change_status(project.id, ProjectStatus.active)
                st.rerun()
        elif project.status == ProjectStatus.completed:
            st.caption("Proyecto completado.")
        else:
            st.markdown("**Activar proyecto**")
            onboarding_date = st.date_input(
                "Fecha de onboarding",
                value=today,
                key=f"onb_{project.id}",
            )
            if st.button("Activar", key=f"act_{project.id}"):
                if project.id is None:
                    st.error("El proyecto no tiene ID.")
                else:
                    tasks = generate_base_tasks(project.id, onboarding_date)
                    tasks.extend(
                        generate_checkups(
                            project.id, onboarding_date, project.duration_weeks
                        )
                    )
                    tasks.extend(
                        generate_closing_tasks(
                            project.id, onboarding_date, project.duration_weeks
                        )
                    )

                    role_to_member: dict[str, int] = {}
                    for a in proj_assignments:
                        role_to_member[a.role] = a.member_id

                    for t in tasks:
                        if t.assigned_to is None:
                            from regrow.domain.templates import BASE_TASKS

                            for tmpl in BASE_TASKS:
                                if tmpl.name == t.title:
                                    t.assigned_to = role_to_member.get(tmpl.role)
                                    break

                    with Session(engine) as session:
                        db_project = session.get(ProjectDB, project.id)
                        if db_project is None:
                            st.error("Proyecto no encontrado.")
                        else:
                            db_project.status = ProjectStatus.active
                            db_project.activated_at = onboarding_date
                            for t in tasks:
                                session.add(
                                    TaskDB(
                                        project_id=t.project_id,
                                        title=t.title,
                                        description=t.description,
                                        notes=t.notes,
                                        status=t.status,
                                        assigned_to=t.assigned_to,
                                        due_date=t.due_date,
                                        is_auto_generated=t.is_auto_generated,
                                    )
                                )
                            session.commit()
                    st.success(f"Proyecto activado. {len(tasks)} tareas generadas.")
                    st.rerun()
