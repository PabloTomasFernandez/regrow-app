import streamlit as st
from sqlmodel import Session, select

from regrow.adapters.db.engine import engine
from regrow.adapters.db.models import ClientDB, CompanyDB

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
    all_clients = list(session.exec(select(ClientDB)).all())

clients_count_by_company: dict[int, int] = {}
for c in all_clients:
    clients_count_by_company[c.company_id] = (
        clients_count_by_company.get(c.company_id, 0) + 1
    )

if not companies:
    st.info("Todavía no hay empresas cargadas.")

for company in companies:
    if company.id is None:
        continue
    cid: int = company.id
    n_clients = clients_count_by_company.get(cid, 0)
    edit_key = f"editing_company_{cid}"
    confirm_key = f"confirm_delete_company_{cid}"
    is_editing = st.session_state.get(edit_key, False)
    is_confirming = st.session_state.get(confirm_key, False)

    with st.container(border=True):
        row = st.columns([3, 2, 2, 2, 1, 1])
        row[0].markdown(f"**{company.name}**")
        row[1].markdown(f"Industria: {company.industry or '—'}")
        row[2].markdown(f"Web: {company.website or '—'}")
        row[3].markdown(f"LinkedIn: {company.linkedin_company or '—'}")

        if row[4].button("Editar", key=f"edit_company_{cid}"):
            st.session_state[edit_key] = True
            st.rerun()

        delete_clicked = row[5].button("Eliminar", key=f"delete_company_{cid}")

        if delete_clicked:
            if n_clients > 0:
                st.warning(
                    f"Esta empresa tiene {n_clients} cliente(s) asociado(s). "
                    "Eliminá primero los clientes."
                )
            else:
                st.session_state[confirm_key] = True
                st.rerun()

        if is_editing:
            with st.form(f"edit_company_form_{cid}"):
                new_name = st.text_input("Nombre *", value=company.name)
                new_industry = st.text_input("Industria", value=company.industry or "")
                new_website = st.text_input("Website", value=company.website or "")
                new_linkedin = st.text_input(
                    "LinkedIn company", value=company.linkedin_company or ""
                )
                col_save, col_cancel = st.columns(2)
                save = col_save.form_submit_button("Guardar")
                cancel = col_cancel.form_submit_button("Cancelar")

                if save:
                    if not new_name.strip():
                        st.error("El nombre es obligatorio.")
                    else:
                        with Session(engine) as session:
                            db_company = session.get(CompanyDB, cid)
                            if db_company is not None:
                                db_company.name = new_name.strip()
                                db_company.industry = new_industry.strip() or None
                                db_company.website = new_website.strip() or None
                                db_company.linkedin_company = (
                                    new_linkedin.strip() or None
                                )
                                session.commit()
                        st.session_state[edit_key] = False
                        st.success("Empresa actualizada.")
                        st.rerun()
                if cancel:
                    st.session_state[edit_key] = False
                    st.rerun()

        if is_confirming:
            st.warning(
                "⚠️ Esta acción eliminará la empresa de forma permanente. "
                "No se puede deshacer."
            )
            col_confirm, col_cancel = st.columns(2)
            if col_confirm.button(
                "Confirmar eliminación", key=f"confirm_del_company_{cid}"
            ):
                with Session(engine) as session:
                    db_company = session.get(CompanyDB, cid)
                    if db_company is not None:
                        session.delete(db_company)
                        session.commit()
                st.session_state[confirm_key] = False
                st.success(f"Empresa '{company.name}' eliminada.")
                st.rerun()
            if col_cancel.button("Cancelar", key=f"cancel_del_company_{cid}"):
                st.session_state[confirm_key] = False
                st.rerun()
