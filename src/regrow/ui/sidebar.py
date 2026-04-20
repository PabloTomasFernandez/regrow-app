import streamlit as st
from sqlmodel import Session, select

from regrow.adapters.db.engine import engine
from regrow.adapters.db.models import TeamMemberDB


def render_viewer_selector() -> None:
    with Session(engine) as session:
        members = list(
            session.exec(
                select(TeamMemberDB).where(TeamMemberDB.active == True)  # noqa: E712
            ).all()
        )

    if not members:
        st.sidebar.warning("No hay miembros activos. Creá uno en la página Equipo.")
        return

    options: dict[str, int] = {}
    for m in members:
        if m.id is None:
            continue
        prefix = "👑" if m.is_admin else f"[{m.role}]"
        options[f"{prefix} {m.name}"] = m.id
    labels = list(options.keys())

    current_id = st.session_state.get("current_viewer_id")
    if current_id not in options.values():
        admin_id = next(
            (m.id for m in members if m.is_admin and m.id is not None), None
        )
        fallback_id = next((m.id for m in members if m.id is not None), None)
        current_id = admin_id if admin_id is not None else fallback_id
        st.session_state["current_viewer_id"] = current_id

    current_label = next(
        (lbl for lbl, vid in options.items() if vid == current_id), labels[0]
    )
    current_idx = labels.index(current_label)

    selected = st.sidebar.selectbox("Viendo como:", labels, index=current_idx)
    st.session_state["current_viewer_id"] = options[selected]

    viewer_id = st.session_state["current_viewer_id"]
    viewer = next((m for m in members if m.id == viewer_id), None)
    if viewer is not None:
        if viewer.is_admin:
            st.sidebar.markdown("**👑 Admin**")
        else:
            st.sidebar.markdown(f"Rol: `{viewer.role}`")

    st.sidebar.divider()
    st.sidebar.caption(
        "Esta es una vista interna. Los permisos son convencionales, no de seguridad."
    )
