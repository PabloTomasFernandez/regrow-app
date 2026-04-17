import streamlit as st
from sqlmodel import Session, select

from regrow.adapters.db.engine import engine
from regrow.adapters.db.models import ClientDB, CompanyDB, ProjectDB

st.set_page_config(page_title="Clientes — Regrow", layout="wide")
st.title("Clientes")

with Session(engine) as session:
    companies = list(session.exec(select(CompanyDB)).all())

if not companies:
    st.warning("Primero tenés que crear al menos una empresa.")
    st.stop()

company_by_label = {f"{c.name} (id {c.id})": c for c in companies}
company_labels = list(company_by_label.keys())

with st.form("create_client", clear_on_submit=True):
    st.subheader("Crear cliente")
    company_label = st.selectbox("Empresa *", company_labels)
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
    all_projects = list(session.exec(select(ProjectDB)).all())

projects_count_by_client: dict[int, int] = {}
for p in all_projects:
    projects_count_by_client[p.client_id] = (
        projects_count_by_client.get(p.client_id, 0) + 1
    )

if not clients:
    st.info("Todavía no hay clientes cargados.")


def company_label_for(company_id: int) -> str:
    company = companies_by_id.get(company_id)
    if company is None:
        return "—"
    return f"{company.name} (id {company.id})"


for client in clients:
    if client.id is None:
        continue
    clid: int = client.id
    n_projects = projects_count_by_client.get(clid, 0)
    edit_key = f"editing_client_{clid}"
    confirm_key = f"confirm_delete_client_{clid}"
    is_editing = st.session_state.get(edit_key, False)
    is_confirming = st.session_state.get(confirm_key, False)

    company = companies_by_id.get(client.company_id)
    company_name = company.name if company else "—"

    with st.container(border=True):
        row = st.columns([3, 2, 3, 2, 1, 1])
        row[0].markdown(f"**{client.name} {client.apellido}**")
        row[1].markdown(f"Empresa: {company_name}")
        row[2].markdown(f"Email: {client.email or '—'}")
        row[3].markdown(f"LinkedIn: {client.linkedin_profile or '—'}")

        if row[4].button("Editar", key=f"edit_client_{clid}"):
            st.session_state[edit_key] = True
            st.rerun()

        delete_clicked = row[5].button("Eliminar", key=f"delete_client_{clid}")

        if delete_clicked:
            if n_projects > 0:
                st.warning(
                    f"Este cliente tiene {n_projects} proyecto(s) asociado(s). "
                    "Eliminá primero los proyectos."
                )
            else:
                st.session_state[confirm_key] = True
                st.rerun()

        if is_editing:
            with st.form(f"edit_client_form_{clid}"):
                new_name = st.text_input("Nombre *", value=client.name)
                new_apellido = st.text_input("Apellido *", value=client.apellido)
                new_email = st.text_input("Email", value=client.email or "")
                new_linkedin = st.text_input(
                    "LinkedIn profile", value=client.linkedin_profile or ""
                )
                current_company_label = company_label_for(client.company_id)
                current_idx = (
                    company_labels.index(current_company_label)
                    if current_company_label in company_labels
                    else 0
                )
                new_company_label = st.selectbox(
                    "Empresa *", company_labels, index=current_idx
                )
                col_save, col_cancel = st.columns(2)
                save = col_save.form_submit_button("Guardar")
                cancel = col_cancel.form_submit_button("Cancelar")

                if save:
                    if not new_name.strip() or not new_apellido.strip():
                        st.error("Nombre y apellido son obligatorios.")
                    else:
                        new_company = company_by_label[new_company_label]
                        if new_company.id is None:
                            st.error("La empresa seleccionada no tiene ID.")
                        else:
                            with Session(engine) as session:
                                db_client = session.get(ClientDB, clid)
                                if db_client is not None:
                                    db_client.name = new_name.strip()
                                    db_client.apellido = new_apellido.strip()
                                    db_client.email = new_email.strip() or None
                                    db_client.linkedin_profile = (
                                        new_linkedin.strip() or None
                                    )
                                    db_client.company_id = new_company.id
                                    session.commit()
                            st.session_state[edit_key] = False
                            st.success("Cliente actualizado.")
                            st.rerun()
                if cancel:
                    st.session_state[edit_key] = False
                    st.rerun()

        if is_confirming:
            st.warning(
                "⚠️ Esta acción eliminará el cliente de forma permanente. "
                "No se puede deshacer."
            )
            col_confirm, col_cancel = st.columns(2)
            if col_confirm.button(
                "Confirmar eliminación", key=f"confirm_del_client_{clid}"
            ):
                with Session(engine) as session:
                    db_client = session.get(ClientDB, clid)
                    if db_client is not None:
                        session.delete(db_client)
                        session.commit()
                st.session_state[confirm_key] = False
                st.success(f"Cliente '{client.name} {client.apellido}' eliminado.")
                st.rerun()
            if col_cancel.button("Cancelar", key=f"cancel_del_client_{clid}"):
                st.session_state[confirm_key] = False
                st.rerun()
