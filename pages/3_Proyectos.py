from datetime import date

import streamlit as st
from sqlmodel import Session, select

from regrow.adapters.db.engine import engine
from regrow.adapters.db.models import ClientDB, CompanyDB, ProjectDB, TaskDB
from regrow.domain.models import ProjectStatus
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

if not clients:
    st.warning("Primero tenés que crear al menos un cliente.")
    st.stop()


def client_label(client: ClientDB) -> str:
    company = companies_by_id.get(client.company_id)
    company_name = company.name if company else "—"
    return f"{client.name} {client.apellido} · {company_name} (id {client.id})"


client_by_label = {client_label(c): c for c in clients}

with st.form("create_project", clear_on_submit=True):
    st.subheader("Crear proyecto")
    label = st.selectbox("Cliente *", list(client_by_label.keys()))
    name = st.text_input("Nombre del proyecto *")
    duration_weeks = st.number_input(
        "Duración (semanas)", min_value=1, max_value=52, value=14, step=1
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
                st.success(f"Proyecto '{name}' creado.")
                st.rerun()

st.subheader("Listado de proyectos")

with Session(engine) as session:
    projects = list(session.exec(select(ProjectDB)).all())
    clients_by_id = {c.id: c for c in session.exec(select(ClientDB)).all()}
    tasks_by_project: dict[int, int] = {}
    for task in session.exec(select(TaskDB)).all():
        tasks_by_project[task.project_id] = tasks_by_project.get(task.project_id, 0) + 1

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

        if project.status == ProjectStatus.active:
            week = current_week(project.activated_at, today)
            task_count = tasks_by_project.get(project.id or 0, 0)
            st.metric("Semana actual", f"{week}/{project.duration_weeks}")
            st.metric("Tareas", task_count)
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
