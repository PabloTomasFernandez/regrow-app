import streamlit as st
from sqlmodel import Session, select

from regrow.adapters.db.engine import engine
from regrow.adapters.db.models import (
    BuyerPersonaDB,
    CampaignDetailDB,
    ClientDB,
    CompanyDB,
    ProjectDB,
)
from regrow.domain.models import CampaignType, CopyStatus, ProjectStatus

st.set_page_config(page_title="Campañas — Regrow", layout="wide")
st.title("Campañas")

with Session(engine) as session:
    active_projects = list(
        session.exec(
            select(ProjectDB).where(ProjectDB.status == ProjectStatus.active)
        ).all()
    )
    clients_by_id = {c.id: c for c in session.exec(select(ClientDB)).all()}
    companies_by_id = {c.id: c for c in session.exec(select(CompanyDB)).all()}

if not active_projects:
    st.warning("No hay proyectos activos. Activá un proyecto primero.")
    st.stop()


def project_label(project: ProjectDB) -> str:
    client = clients_by_id.get(project.client_id)
    company_name = "—"
    if client is not None:
        company = companies_by_id.get(client.company_id)
        if company is not None:
            company_name = company.name
    return f"{project.name} — {company_name} (id {project.id})"


project_by_label = {project_label(p): p for p in active_projects}
selected_label = st.selectbox("Proyecto *", list(project_by_label.keys()))
selected_project = project_by_label[selected_label]

if selected_project.id is None:
    st.error("El proyecto seleccionado no tiene ID.")
    st.stop()

project_id: int = selected_project.id

st.subheader("Crear campaña")
with st.form("create_campaign", clear_on_submit=True):
    number = st.number_input("Número de campaña *", min_value=1, step=1, value=1)
    campaign_type = st.selectbox(
        "Tipo", [CampaignType.normal.value, CampaignType.event.value]
    )
    industry = st.text_input("Industria *")
    country = st.text_input("País *")
    company_size = st.text_input("Tamaño de empresa")
    event_name = st.text_input("Nombre del evento (solo si tipo = event)")
    submitted = st.form_submit_button("Crear campaña")

    if submitted:
        if not industry.strip() or not country.strip():
            st.error("Industria y país son obligatorios.")
        elif campaign_type == CampaignType.event.value and not event_name.strip():
            st.error("El nombre del evento es obligatorio para campañas tipo event.")
        else:
            with Session(engine) as session:
                campaign = CampaignDetailDB(
                    project_id=project_id,
                    number=int(number),
                    campaign_type=campaign_type,
                    industry=industry.strip(),
                    country=country.strip(),
                    company_size=company_size.strip(),
                    event_name=event_name.strip() or None,
                )
                session.add(campaign)
                session.commit()
            st.success(f"Campaña #{int(number)} creada.")
            st.rerun()

st.subheader("Campañas del proyecto")

with Session(engine) as session:
    campaigns = list(
        session.exec(
            select(CampaignDetailDB).where(CampaignDetailDB.project_id == project_id)
        ).all()
    )
    all_bps = list(session.exec(select(BuyerPersonaDB)).all())

bps_by_campaign: dict[int, list[BuyerPersonaDB]] = {}
for bp in all_bps:
    bps_by_campaign.setdefault(bp.campaign_detail_id, []).append(bp)

if not campaigns:
    st.info("Este proyecto todavía no tiene campañas.")

NEXT_STATUS = {
    CopyStatus.draft.value: CopyStatus.in_review.value,
    CopyStatus.in_review.value: CopyStatus.validated.value,
    CopyStatus.validated.value: CopyStatus.draft.value,
}

for campaign in campaigns:
    if campaign.id is None:
        continue
    campaign_id: int = campaign.id
    header = (
        f"Campaña #{campaign.number} · {campaign.industry} / {campaign.country}"
        f" · `{campaign.copy_status}`"
    )
    with st.expander(header):
        st.markdown(
            f"**Tipo:** {campaign.campaign_type}  \n"
            f"**Tamaño:** {campaign.company_size or '—'}  \n"
            f"**Evento:** {campaign.event_name or '—'}"
        )

        st.markdown("**Agregar buyer persona**")
        with st.form(f"create_bp_{campaign_id}", clear_on_submit=True):
            position = st.text_input("Position *", key=f"pos_{campaign_id}")
            trigger = st.text_input("Trigger", key=f"trg_{campaign_id}")
            attendee_type = st.text_input(
                "Attendee type (solo eventos)", key=f"att_{campaign_id}"
            )
            bp_submitted = st.form_submit_button("Agregar buyer persona")

            if bp_submitted:
                if not position.strip():
                    st.error("Position es obligatorio.")
                else:
                    with Session(engine) as session:
                        bp = BuyerPersonaDB(
                            campaign_detail_id=campaign_id,
                            position=position.strip(),
                            trigger=trigger.strip() or None,
                            attendee_type=attendee_type.strip() or None,
                        )
                        session.add(bp)
                        session.commit()
                    st.success(f"Buyer persona '{position}' agregado.")
                    st.rerun()

        st.markdown("**Buyer personas**")
        campaign_bps = bps_by_campaign.get(campaign_id, [])
        if not campaign_bps:
            st.caption("Sin buyer personas.")
        for bp in campaign_bps:
            if bp.id is None:
                continue
            bp_id: int = bp.id
            cols = st.columns([3, 2, 2, 2])
            cols[0].markdown(f"**{bp.position}**")
            cols[1].markdown(f"Trigger: {bp.trigger or '—'}")
            cols[2].markdown(f"Status: `{bp.status}`")
            next_status = NEXT_STATUS.get(bp.status, CopyStatus.draft.value)
            if cols[3].button(
                f"→ {next_status}",
                key=f"bp_status_{bp_id}",
            ):
                with Session(engine) as session:
                    db_bp = session.get(BuyerPersonaDB, bp_id)
                    if db_bp is not None:
                        db_bp.status = next_status
                        session.commit()
                st.rerun()
