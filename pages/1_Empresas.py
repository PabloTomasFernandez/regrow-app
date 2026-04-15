import streamlit as st
from sqlmodel import Session, select

from regrow.adapters.db.engine import engine
from regrow.adapters.db.models import CompanyDB

st.set_page_config(page_title="Empresas — Regrow", layout="wide")
st.title("Empresas")

with st.form("create_company", clear_on_submit=True):
    st.subheader("Crear empresa")
    name = st.text_input("Nombre *")
    industry = st.text_input("Industria")
    website = st.text_input("Website")
    linkedin_company = st.text_input("LinkedIn company")
    submitted = st.form_submit_button("Crear empresa")

    if submitted:
        if not name.strip():
            st.error("El nombre es obligatorio.")
        else:
            with Session(engine) as session:
                company = CompanyDB(
                    name=name.strip(),
                    industry=industry.strip() or None,
                    website=website.strip() or None,
                    linkedin_company=linkedin_company.strip() or None,
                )
                session.add(company)
                session.commit()
            st.success(f"Empresa '{name}' creada.")
            st.rerun()

st.subheader("Listado de empresas")
with Session(engine) as session:
    companies = list(session.exec(select(CompanyDB)).all())

if not companies:
    st.info("Todavía no hay empresas cargadas.")
else:
    rows = [
        {
            "ID": c.id,
            "Nombre": c.name,
            "Industria": c.industry or "—",
            "Website": c.website or "—",
            "LinkedIn": c.linkedin_company or "—",
        }
        for c in companies
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)  # pyright: ignore[reportUnknownMemberType]
