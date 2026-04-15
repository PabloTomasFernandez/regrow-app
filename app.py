from datetime import date
from typing import Any

import pandas as pd  # pyright: ignore[reportMissingTypeStubs]
import streamlit as st
from sqlmodel import Session, select

from regrow.adapters.db.engine import engine
from regrow.adapters.db.models import (
    BuyerPersonaDB,
    CampaignDetailDB,
    ClientDB,
    CompanyDB,
    ProjectDB,
    TaskDB,
)
from regrow.domain.models import TaskStatus


def current_week(activated_at: date | None, today: date) -> int:
    if activated_at is None:
        return 0
    return max(1, (today - activated_at).days // 7 + 1)


def load_data() -> dict[str, object]:
    today = date.today()
    with Session(engine) as session:
        projects = list(session.exec(select(ProjectDB)).all())
        clients = {c.id: c for c in session.exec(select(ClientDB)).all()}
        companies = {c.id: c for c in session.exec(select(CompanyDB)).all()}
        campaigns = list(session.exec(select(CampaignDetailDB)).all())
        bps = list(session.exec(select(BuyerPersonaDB)).all())
        tasks = list(session.exec(select(TaskDB)).all())

    campaigns_by_project: dict[int, list[CampaignDetailDB]] = {}
    for c in campaigns:
        campaigns_by_project.setdefault(c.project_id, []).append(c)

    bps_by_campaign: dict[int, list[BuyerPersonaDB]] = {}
    for bp in bps:
        bps_by_campaign.setdefault(bp.campaign_detail_id, []).append(bp)

    tasks_by_project: dict[int, list[TaskDB]] = {}
    for t in tasks:
        tasks_by_project.setdefault(t.project_id, []).append(t)

    return {
        "today": today,
        "projects": projects,
        "clients": clients,
        "companies": companies,
        "campaigns_by_project": campaigns_by_project,
        "bps_by_campaign": bps_by_campaign,
        "tasks_by_project": tasks_by_project,
    }


def project_metrics(
    project: ProjectDB,
    data: dict[str, object],
) -> dict[str, object]:
    today: date = data["today"]  # type: ignore[assignment]
    campaigns_by_project: dict[int, list[CampaignDetailDB]] = (
        data["campaigns_by_project"]  # type: ignore[assignment]
    )
    bps_by_campaign: dict[int, list[BuyerPersonaDB]] = data["bps_by_campaign"]  # type: ignore[assignment]
    tasks_by_project: dict[int, list[TaskDB]] = data["tasks_by_project"]  # type: ignore[assignment]

    pid = project.id or 0
    project_campaigns = campaigns_by_project.get(pid, [])
    pending_bps = 0
    for camp in project_campaigns:
        for bp in bps_by_campaign.get(camp.id or 0, []):
            if bp.status != "validated":
                pending_bps += 1

    overdue_tasks = [
        t
        for t in tasks_by_project.get(pid, [])
        if t.due_date is not None
        and t.due_date < today
        and t.status != TaskStatus.done
    ]

    return {
        "campaigns": project_campaigns,
        "pending_bps": pending_bps,
        "overdue_tasks": overdue_tasks,
    }


def main() -> None:
    st.set_page_config(page_title="Regrow", layout="wide")
    st.title("Regrow — Panel de control")

    data = load_data()
    today: date = data["today"]  # type: ignore[assignment]
    all_projects: list[ProjectDB] = data["projects"]  # type: ignore[assignment]
    clients: dict[int, ClientDB] = data["clients"]  # type: ignore[assignment]
    companies: dict[int, CompanyDB] = data["companies"]  # type: ignore[assignment]
    bps_by_campaign: dict[int, list[BuyerPersonaDB]] = data["bps_by_campaign"]  # type: ignore[assignment]

    status_options = ["all", "active", "completed", "paused"]
    selected_status = st.selectbox("Filtrar por estado", status_options, index=0)
    if selected_status == "all":
        projects = all_projects
    else:
        projects = [p for p in all_projects if str(p.status) == selected_status]

    total_projects = len(projects)
    total_campaigns = 0
    total_pending_bps = 0
    total_overdue = 0

    rows: list[dict[str, object]] = []
    per_project: dict[int, dict[str, object]] = {}

    for p in projects:
        m = project_metrics(p, data)
        project_campaigns: list[CampaignDetailDB] = m["campaigns"]  # type: ignore[assignment]
        pending_bps: int = m["pending_bps"]  # type: ignore[assignment]
        overdue_tasks: list[TaskDB] = m["overdue_tasks"]  # type: ignore[assignment]

        total_campaigns += len(project_campaigns)
        total_pending_bps += pending_bps
        total_overdue += len(overdue_tasks)

        client = clients.get(p.client_id)
        company = companies.get(client.company_id) if client else None
        company_name = company.name if company else "—"

        rows.append(
            {
                "Cliente": company_name,
                "Proyecto": p.name,
                "Semana": current_week(p.activated_at, today),
                "Duración": p.duration_weeks,
                "Campañas": len(project_campaigns),
                "BPs pendientes": pending_bps,
                "Tareas vencidas": len(overdue_tasks),
                "Estado": str(p.status),
            }
        )
        per_project[p.id or 0] = {
            "project": p,
            "company_name": company_name,
            "campaigns": project_campaigns,
            "overdue_tasks": overdue_tasks,
        }

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(label="Proyectos activos", value=total_projects)
    c2.metric(label="Campañas", value=total_campaigns)
    c3.metric(label="BPs pendientes", value=total_pending_bps)
    c4.metric(label="Tareas vencidas", value=total_overdue)

    st.subheader("Proyectos")
    rows.sort(key=lambda r: r["Tareas vencidas"], reverse=True)  # type: ignore[arg-type,return-value]
    df = pd.DataFrame(rows)

    def highlight_overdue(row: Any) -> list[str]:
        color = "background-color: #5a1a1a" if row["Tareas vencidas"] > 0 else ""
        return [color] * len(row)

    if not df.empty:
        styled: Any = df.style.apply(highlight_overdue, axis=1)  # pyright: ignore[reportUnknownMemberType]
        st.dataframe(styled, use_container_width=True, hide_index=True)  # pyright: ignore[reportUnknownMemberType]
    else:
        st.info("No hay proyectos activos.")

    st.subheader("Detalle de proyectos")
    for _pid, info in per_project.items():
        project: ProjectDB = info["project"]  # type: ignore[assignment]
        company_name: str = info["company_name"]  # type: ignore[assignment]
        project_campaigns: list[CampaignDetailDB] = info["campaigns"]  # type: ignore[assignment]
        overdue_tasks: list[TaskDB] = info["overdue_tasks"]  # type: ignore[assignment]
        week = current_week(project.activated_at, today)

        label = (
            f"{company_name} — {project.name}"
            f" (semana {week}/{project.duration_weeks})"
        )
        with st.expander(label):
            if week > project.duration_weeks:
                st.warning("⚠️ Proyecto pasado de fecha")
            st.markdown(
                f"**Cliente:** {company_name}  \n"
                f"**Proyecto:** {project.name}  \n"
                f"**Semana:** {week} de {project.duration_weeks}  \n"
                f"**Activado:** {project.activated_at}  \n"
                f"**Estado:** {project.status}"
            )

            st.markdown("**Campañas**")
            if not project_campaigns:
                st.caption("Sin campañas.")
            for camp in project_campaigns:
                camp_bps = bps_by_campaign.get(camp.id or 0, [])
                st.markdown(
                    f"- Campaña #{camp.number} · {camp.industry} / {camp.country}"
                    f" · copy: `{camp.copy_status}`"
                )
                for bp in camp_bps:
                    st.markdown(f"    - {bp.position} — `{bp.status}`")

            st.markdown("**Tareas vencidas**")
            if not overdue_tasks:
                st.caption("Ninguna.")
            for t in overdue_tasks:
                st.markdown(f"- {t.title} — venció {t.due_date}")


if __name__ == "__main__":
    main()
