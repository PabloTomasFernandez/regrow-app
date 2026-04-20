import streamlit as st
from sqlmodel import Session

from regrow.adapters.db.engine import engine
from regrow.adapters.db.models import TeamMemberDB


def current_viewer() -> TeamMemberDB | None:
    viewer_id = st.session_state.get("current_viewer_id")
    if viewer_id is None:
        return None
    with Session(engine) as session:
        return session.get(TeamMemberDB, viewer_id)
