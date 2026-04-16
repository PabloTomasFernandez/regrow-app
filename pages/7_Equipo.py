import streamlit as st
from sqlmodel import Session, select

from regrow.adapters.db.engine import engine
from regrow.adapters.db.models import TeamMemberDB
from regrow.domain.models import TeamRole

st.set_page_config(page_title="Equipo — Regrow", layout="wide")
st.title("Equipo")

ROLE_LABELS: list[tuple[str, TeamRole]] = [
    ("Account Manager", TeamRole.account_manager),
    ("SDR", TeamRole.sdr),
    ("Copy", TeamRole.copy),
    ("COO", TeamRole.coo),
    ("Pusher", TeamRole.pusher),
    ("Automater", TeamRole.automater),
]
ROLE_DISPLAY = [label for label, _ in ROLE_LABELS]
ROLE_VALUES = [role for _, role in ROLE_LABELS]

# --- Crear miembro ---
with st.form("create_member", clear_on_submit=True):
    st.subheader("Agregar miembro")
    new_name = st.text_input("Nombre *")
    new_role_label = st.selectbox("Rol *", ROLE_DISPLAY, key="new_role")
    new_email = st.text_input("Email")
    new_admin = st.checkbox("Es admin", value=False)
    submitted = st.form_submit_button("Crear miembro")

    if submitted:
        if not new_name.strip():
            st.error("El nombre es obligatorio.")
        else:
            role_value = ROLE_VALUES[ROLE_DISPLAY.index(new_role_label)]
            with Session(engine) as session:
                session.add(
                    TeamMemberDB(
                        name=new_name.strip(),
                        role=role_value,
                        email=new_email.strip() or None,
                        is_admin=new_admin,
                    )
                )
                session.commit()
            st.success(f"Miembro '{new_name.strip()}' creado.")
            st.rerun()

st.divider()

# --- Listado ---
st.subheader("Miembros del equipo")

show_inactive = st.checkbox("Mostrar inactivos", value=False)

with Session(engine) as session:
    if show_inactive:
        members = list(session.exec(select(TeamMemberDB)).all())
    else:
        members = list(
            session.exec(
                select(TeamMemberDB).where(TeamMemberDB.active == True)  # noqa: E712
            ).all()
        )

if not members:
    st.info("No hay miembros cargados.")
else:
    header = st.columns([1, 3, 2, 3, 1, 1, 3])
    for col, text in zip(
        header,
        ["ID", "Nombre", "Rol", "Email", "Admin", "Activo", ""],
        strict=True,
    ):
        col.markdown(f"**{text}**")

    for m in members:
        row = st.columns([1, 3, 2, 3, 1, 1, 3])
        row[0].markdown(str(m.id))
        row[1].markdown(m.name)
        role_display = (
            ROLE_DISPLAY[ROLE_VALUES.index(m.role)] if m.role in ROLE_VALUES else m.role
        )
        row[2].markdown(role_display)
        row[3].markdown(m.email or "—")
        row[4].markdown("✓" if m.is_admin else "")
        row[5].markdown("✓" if m.active else "✗")

        btn_col = row[6]
        c1, c2 = btn_col.columns(2)

        if c1.button("Editar", key=f"edit_btn_{m.id}"):
            st.session_state[f"editing_{m.id}"] = True

        if m.active:
            if c2.button("Desactivar", key=f"deact_{m.id}"):
                with Session(engine) as session:
                    db_m = session.get(TeamMemberDB, m.id)
                    if db_m is not None:
                        db_m.active = False
                        session.commit()
                st.rerun()
        else:
            if c2.button("Activar", key=f"act_{m.id}"):
                with Session(engine) as session:
                    db_m = session.get(TeamMemberDB, m.id)
                    if db_m is not None:
                        db_m.active = True
                        session.commit()
                st.rerun()

        if st.session_state.get(f"editing_{m.id}", False):
            with st.form(f"edit_form_{m.id}"):
                edit_name = st.text_input("Nombre", value=m.name, key=f"en_{m.id}")
                current_role_idx = (
                    ROLE_VALUES.index(m.role) if m.role in ROLE_VALUES else 0
                )
                edit_role_label = st.selectbox(
                    "Rol",
                    ROLE_DISPLAY,
                    index=current_role_idx,
                    key=f"er_{m.id}",
                )
                edit_email = st.text_input(
                    "Email", value=m.email or "", key=f"ee_{m.id}"
                )
                edit_admin = st.checkbox("Es admin", value=m.is_admin, key=f"ea_{m.id}")
                save_cols = st.columns(2)
                save = save_cols[0].form_submit_button("Guardar")
                cancel = save_cols[1].form_submit_button("Cancelar")

                if save:
                    role_value = ROLE_VALUES[ROLE_DISPLAY.index(edit_role_label)]
                    with Session(engine) as session:
                        db_m = session.get(TeamMemberDB, m.id)
                        if db_m is not None:
                            db_m.name = edit_name.strip()
                            db_m.role = role_value
                            db_m.email = edit_email.strip() or None
                            db_m.is_admin = edit_admin
                            session.commit()
                    st.session_state[f"editing_{m.id}"] = False
                    st.rerun()

                if cancel:
                    st.session_state[f"editing_{m.id}"] = False
                    st.rerun()
