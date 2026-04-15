import streamlit as st
from sqlmodel import Session, select

from regrow.adapters.db.engine import engine
from regrow.adapters.db.models import ClientDB, CompanyDB

st.set_page_config(page_title="Clientes — Regrow", layout="wide")
st.title("Clientes")

with Session(engine) as session:
    companies = list(session.exec(select(CompanyDB)).all())

if not companies:
    st.warning("Primero tenés que crear al menos una empresa.")
    st.stop()

company_by_label = {f"{c.name} (id {c.id})": c for c in companies}

with st.form("create_client", clear_on_submit=True):
    st.subheader("Crear cliente")
    company_label = st.selectbox("Empresa *", list(company_by_label.keys()))
    name = st.text_input("Nombre *")
    apellido = st.text_input("Apellido *")
    email = st.text_input("Email")
    linkedin_profile = st.text_input("LinkedIn profile")
    submitted = st.form_submit_button("Crear cliente")

    if submitted:
        if not name.strip() or not apellido.strip():
            st.error("Nombre y apellido son obligatorios.")
        else:
            company = company_by_label[company_label]
            if company.id is None:
                st.error("La empresa seleccionada no tiene ID.")
            else:
                with Session(engine) as session:
                    client = ClientDB(
                        name=name.strip(),
                        apellido=apellido.strip(),
                        email=email.strip() or None,
                        company_id=company.id,
                        linkedin_profile=linkedin_profile.strip() or None,
                    )
                    session.add(client)
                    session.commit()
                st.success(f"Cliente '{name} {apellido}' creado.")
                st.rerun()

st.subheader("Listado de clientes")
with Session(engine) as session:
    clients = list(session.exec(select(ClientDB)).all())
    companies_by_id = {c.id: c for c in session.exec(select(CompanyDB)).all()}

if not clients:
    st.info("Todavía no hay clientes cargados.")
else:
    rows = [
        {
            "ID": c.id,
            "Nombre": f"{c.name} {c.apellido}",
            "Empresa": (
                companies_by_id[c.company_id].name
                if c.company_id in companies_by_id
                else "—"
            ),
            "Email": c.email or "—",
            "LinkedIn": c.linkedin_profile or "—",
        }
        for c in clients
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)  # pyright: ignore[reportUnknownMemberType]
