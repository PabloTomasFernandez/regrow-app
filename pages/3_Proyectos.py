from datetime import date

import streamlit as st
from sqlmodel import Session, select, update

from regrow.adapters.db.engine import engine
from regrow.adapters.db.models import (
    AssignmentDB,
    BuyerPersonaDB,
    CampaignDetailDB,
    ClientDB,
    CompanyDB,
    MessageDB,
    ProjectDB,
    SequenceDB,
    TaskDB,
    TaskTemplateDB,
    TeamMemberDB,
    ValidationDB,
)
from regrow.domain.models import CampaignType, ProjectStatus, TaskStatus, TeamRole
from regrow.domain.services import (
    generate_base_tasks,
    generate_campaign_tasks,
    generate_checkups,
    generate_closing_tasks,
)
from regrow.domain.templates import CAMPAIGN_NORMAL, CAMPAIGN_START_WEEKS

st.set_page_config(page_title="Proyectos — Regrow", layout="wide")
st.title("Proyectos")


def current_week(activated_at: date | None, today: date) -> int:
    if activated_at is None:
        return 0
    return max(1, (today - activated_at).days // 7 + 1)


def member_label(member: TeamMemberDB) -> str:
    return f"{member.name} (id {member.id})"


def parse_member_id(label_str: str) -> int:
    return int(label_str.split("id ")[-1].rstrip(")"))


ASSIGNMENT_ROLES: list[tuple[str, TeamRole]] = [
    ("Account Manager", TeamRole.account_manager),
    ("SDR", TeamRole.sdr),
    ("Copy", TeamRole.copy),
    ("Pusher", TeamRole.pusher),
    ("Automater", TeamRole.automater),
]

with Session(engine) as session:
    clients = list(session.exec(select(ClientDB)).all())
    companies_by_id = {c.id: c for c in session.exec(select(CompanyDB)).all()}
    all_members = list(session.exec(select(TeamMemberDB)).all())

if not clients:
    st.warning("Primero tenés que crear al menos un cliente.")
    st.stop()

active_members = [m for m in all_members if m.active]

members_by_role: dict[str, list[TeamMemberDB]] = {}
for m in active_members:
    members_by_role.setdefault(m.role, []).append(m)


def client_label(client: ClientDB) -> str:
    company = companies_by_id.get(client.company_id)
    company_name = company.name if company else "—"
    return f"{client.name} {client.apellido} · {company_name} (id {client.id})"


client_by_label = {client_label(c): c for c in clients}

# --- Crear proyecto ---

st.subheader("Crear proyecto")

st.markdown("**Equipo del proyecto**")
for display_name, role_enum in ASSIGNMENT_ROLES:
    candidates = members_by_role.get(role_enum, [])
    if not candidates:
        st.warning(
            f"⚠️ No hay miembros con rol {display_name}. "
            "Creá uno en la página Equipo antes de asignar este rol."
        )
    show_all = st.checkbox(
        f"Mostrar todos los miembros para {display_name}",
        key=f"show_all_{role_enum}",
    )
    if show_all:
        candidates = active_members
    if candidates:
        options = [member_label(m) for m in candidates]
        st.selectbox(
            display_name,
            options,
            key=f"role_{role_enum}",
        )

with st.form("create_project", clear_on_submit=True):
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
                    session.refresh(project)
                    assert project.id is not None

                    for _dn, role_enum in ASSIGNMENT_ROLES:
                        sel = st.session_state.get(f"role_{role_enum}")
                        if sel is not None:
                            mid = parse_member_id(sel)
                            session.add(
                                AssignmentDB(
                                    project_id=project.id,
                                    member_id=mid,
                                    role=role_enum,
                                )
                            )
                    session.commit()
                st.success(f"Proyecto '{name}' creado con equipo asignado.")
                st.rerun()

st.divider()
st.subheader("Listado de proyectos")

with Session(engine) as session:
    projects = list(session.exec(select(ProjectDB)).all())
    clients_by_id = {c.id: c for c in session.exec(select(ClientDB)).all()}
    tasks_by_project_count: dict[int, int] = {}
    all_tasks_list = list(session.exec(select(TaskDB)).all())
    for task in all_tasks_list:
        tasks_by_project_count[task.project_id] = (
            tasks_by_project_count.get(task.project_id, 0) + 1
        )
    all_assignments = list(session.exec(select(AssignmentDB)).all())

tasks_by_project: dict[int, list[TaskDB]] = {}
for t in all_tasks_list:
    tasks_by_project.setdefault(t.project_id, []).append(t)

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

        # --- Cambiar rol en este proyecto ---
        if proj_assignments and project.id is not None:
            st.markdown("**Cambiar rol en este proyecto**")
            for a in proj_assignments:
                cur_member = members_by_id.get(a.member_id)
                cur_name = cur_member.name if cur_member else "?"
                change_key = f"change_{project.id}_{a.id}"

                col_info, col_btn = st.columns([4, 1])
                col_info.markdown(f"`{a.role}`: {cur_name}")
                if col_btn.button("Cambiar", key=change_key):
                    st.session_state[f"changing_{a.id}"] = True

                if st.session_state.get(f"changing_{a.id}", False):
                    role_candidates = members_by_role.get(a.role, [])
                    show_all_r = st.checkbox(
                        "Mostrar todos",
                        key=f"show_all_reassign_{a.id}",
                    )
                    if show_all_r:
                        role_candidates = active_members
                    if not role_candidates:
                        st.warning("No hay miembros activos con este rol.")
                    else:
                        new_sel = st.selectbox(
                            "Nuevo miembro",
                            [member_label(m) for m in role_candidates],
                            key=f"new_member_{a.id}",
                        )
                        c1, c2 = st.columns(2)
                        if c1.button("Confirmar cambio", key=f"confirm_{a.id}"):
                            new_mid = parse_member_id(new_sel)
                            old_mid = a.member_id
                            pid = project.id
                            with Session(engine) as session:
                                session.exec(
                                    update(AssignmentDB)  # type: ignore[call-overload]
                                    .where(AssignmentDB.id == a.id)
                                    .values(member_id=new_mid)
                                )
                                session.exec(
                                    update(TaskDB)  # type: ignore[call-overload]
                                    .where(TaskDB.project_id == pid)
                                    .where(TaskDB.assigned_to == old_mid)
                                    .where(TaskDB.status != TaskStatus.done)
                                    .values(assigned_to=new_mid)
                                )
                                session.commit()
                            st.session_state[f"changing_{a.id}"] = False
                            st.rerun()
                        if c2.button("Cancelar", key=f"cancel_{a.id}"):
                            st.session_state[f"changing_{a.id}"] = False
                            st.rerun()

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
            task_count = tasks_by_project_count.get(project.id or 0, 0)
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
                    from regrow.domain.templates import TaskTemplate

                    with Session(engine) as tmpl_session:
                        db_templates = list(
                            tmpl_session.exec(select(TaskTemplateDB)).all()
                        )

                    tmpl_list: list[TaskTemplate] | None = None
                    if db_templates:
                        tmpl_list = [
                            TaskTemplate(
                                name=tt.title,
                                role=tt.role,
                                week=tt.week,
                            )
                            for tt in db_templates
                            if tt.category == "base"
                        ]

                    tasks = generate_base_tasks(project.id, onboarding_date, tmpl_list)
                    tasks.extend(
                        generate_checkups(
                            project.id,
                            onboarding_date,
                            project.duration_weeks,
                        )
                    )
                    tasks.extend(
                        generate_closing_tasks(
                            project.id,
                            onboarding_date,
                            project.duration_weeks,
                        )
                    )

                    role_to_member: dict[str, int] = {}
                    for a in proj_assignments:
                        role_to_member[a.role] = a.member_id

                    tmpl_role_map: dict[str, str] = {}
                    source = tmpl_list or []
                    if not source:
                        from regrow.domain.templates import BASE_TASKS

                        source = list(BASE_TASKS)
                    for tmpl in source:
                        tmpl_role_map[tmpl.name] = tmpl.role

                    for t in tasks:
                        if t.assigned_to is None:
                            role = tmpl_role_map.get(t.title)
                            if role:
                                t.assigned_to = role_to_member.get(role)

                    campaign_task_count = 0
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
                                        is_auto_generated=(t.is_auto_generated),
                                    )
                                )

                            campaign_task_count = 0
                            for idx, start_week in enumerate(
                                CAMPAIGN_START_WEEKS, start=1
                            ):
                                campaign = CampaignDetailDB(
                                    project_id=project.id,
                                    number=idx,
                                    campaign_type=CampaignType.normal.value,
                                )
                                session.add(campaign)
                                session.flush()
                                assert campaign.id is not None

                                camp_tasks = generate_campaign_tasks(
                                    project_id=project.id,
                                    campaign_start_week=start_week,
                                    onboarding_date=onboarding_date,
                                    campaign_templates=CAMPAIGN_NORMAL,
                                    campaign_label=f"Campaña {idx}",
                                    campaign_id=campaign.id,
                                    role_to_member=role_to_member,
                                )
                                for ct in camp_tasks:
                                    session.add(
                                        TaskDB(
                                            project_id=ct.project_id,
                                            title=ct.title,
                                            description=ct.description,
                                            notes=ct.notes,
                                            status=ct.status,
                                            assigned_to=ct.assigned_to,
                                            due_date=ct.due_date,
                                            is_auto_generated=ct.is_auto_generated,
                                            campaign_id=ct.campaign_id,
                                        )
                                    )
                                campaign_task_count += len(camp_tasks)

                            session.commit()
                    st.success(
                        f"Proyecto activado. {len(tasks)} tareas base + "
                        f"{campaign_task_count} tareas de campaña generadas "
                        "(3 campañas creadas)."
                    )
                    st.rerun()

        if project.status in (ProjectStatus.draft, ProjectStatus.paused):
            st.divider()
            st.markdown("**Eliminar proyecto**")
            del_key = f"deleting_project_{project.id}"
            is_deleting = st.session_state.get(del_key, False)

            if not is_deleting:
                if st.button("Eliminar proyecto", key=f"del_btn_{project.id}"):
                    st.session_state[del_key] = True
                    st.rerun()
            else:
                st.warning(
                    "⚠️ Esto eliminará el proyecto, sus tareas, campañas, "
                    "buyer personas, asignaciones y todo lo asociado. "
                    "Esta acción no se puede deshacer."
                )
                typed = st.text_input(
                    f"Escribí el nombre del proyecto para confirmar: "
                    f"**{project.name}**",
                    key=f"del_name_{project.id}",
                )
                c1, c2 = st.columns(2)
                can_delete = typed == project.name
                if c1.button(
                    "Confirmar eliminación",
                    key=f"confirm_del_proj_{project.id}",
                    disabled=not can_delete,
                ):
                    pid = project.id
                    if pid is not None:
                        with Session(engine) as session:
                            campaigns = list(
                                session.exec(
                                    select(CampaignDetailDB).where(
                                        CampaignDetailDB.project_id == pid
                                    )
                                ).all()
                            )
                            for camp in campaigns:
                                bps = list(
                                    session.exec(
                                        select(BuyerPersonaDB).where(
                                            BuyerPersonaDB.campaign_detail_id == camp.id
                                        )
                                    ).all()
                                )
                                for bp in bps:
                                    seqs = list(
                                        session.exec(
                                            select(SequenceDB).where(
                                                SequenceDB.buyer_persona_id == bp.id
                                            )
                                        ).all()
                                    )
                                    for seq in seqs:
                                        msgs = list(
                                            session.exec(
                                                select(MessageDB).where(
                                                    MessageDB.sequence_id == seq.id
                                                )
                                            ).all()
                                        )
                                        for msg in msgs:
                                            vals = list(
                                                session.exec(
                                                    select(ValidationDB).where(
                                                        ValidationDB.message_id
                                                        == msg.id
                                                    )
                                                ).all()
                                            )
                                            for v in vals:
                                                session.delete(v)
                                            session.delete(msg)
                                        session.delete(seq)
                                    session.delete(bp)

                            for t in session.exec(
                                select(TaskDB).where(TaskDB.project_id == pid)
                            ).all():
                                session.delete(t)

                            for camp in campaigns:
                                session.delete(camp)

                            for a in session.exec(
                                select(AssignmentDB).where(
                                    AssignmentDB.project_id == pid
                                )
                            ).all():
                                session.delete(a)

                            db_proj = session.get(ProjectDB, pid)
                            if db_proj is not None:
                                session.delete(db_proj)
                            session.commit()
                        st.session_state[del_key] = False
                        st.success(f"Proyecto '{project.name}' eliminado.")
                        st.rerun()
                if c2.button("Cancelar", key=f"cancel_del_proj_{project.id}"):
                    st.session_state[del_key] = False
                    st.rerun()
