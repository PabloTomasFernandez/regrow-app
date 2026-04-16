import streamlit as st
from sqlmodel import Session, select

from regrow.adapters.db.engine import engine
from regrow.adapters.db.models import TaskTemplateDB
from regrow.domain.models import TeamRole

st.set_page_config(page_title="Templates — Regrow", layout="wide")
st.title("Templates de tareas")

ROLE_OPTIONS = [r.value for r in TeamRole]
CATEGORY_OPTIONS = ["base", "campaign", "closing", "checkup"]

with Session(engine) as session:
    templates = list(
        session.exec(select(TaskTemplateDB).order_by(TaskTemplateDB.week)).all()  # type: ignore[call-overload]
    )

if not templates:
    st.info("No hay templates cargados. Ejecutá el seed para poblar la tabla.")

st.subheader("Templates actuales")

for t in templates:
    with st.expander(f"Semana {t.week} — {t.title} ({t.role})"):
        with st.form(f"edit_{t.id}"):
            title = st.text_input("Título", value=t.title, key=f"title_{t.id}")
            description = st.text_input(
                "Descripción", value=t.description or "", key=f"desc_{t.id}"
            )
            col1, col2 = st.columns(2)
            role = col1.selectbox(
                "Rol",
                ROLE_OPTIONS,
                index=ROLE_OPTIONS.index(t.role) if t.role in ROLE_OPTIONS else 0,
                key=f"role_{t.id}",
            )
            week = col2.number_input(
                "Semana", min_value=1, max_value=52, value=t.week, key=f"week_{t.id}"
            )
            category = st.selectbox(
                "Categoría",
                CATEGORY_OPTIONS,
                index=(
                    CATEGORY_OPTIONS.index(t.category)
                    if t.category in CATEGORY_OPTIONS
                    else 0
                ),
                key=f"cat_{t.id}",
            )

            btn_cols = st.columns(2)
            save = btn_cols[0].form_submit_button("Guardar cambios")
            delete = btn_cols[1].form_submit_button("Eliminar")

            if save:
                with Session(engine) as session:
                    db_t = session.get(TaskTemplateDB, t.id)
                    if db_t is not None:
                        db_t.title = title.strip()
                        db_t.description = description.strip() or None
                        db_t.role = role
                        db_t.week = int(week)
                        db_t.category = category
                        session.commit()
                st.success("Template actualizado.")
                st.rerun()

            if delete:
                with Session(engine) as session:
                    db_t = session.get(TaskTemplateDB, t.id)
                    if db_t is not None:
                        session.delete(db_t)
                        session.commit()
                st.success("Template eliminado.")
                st.rerun()

st.divider()
st.subheader("Agregar template")

with st.form("add_template", clear_on_submit=True):
    new_title = st.text_input("Título *")
    new_description = st.text_input("Descripción")
    col1, col2 = st.columns(2)
    new_role = col1.selectbox("Rol", ROLE_OPTIONS, key="new_role")
    new_week = col2.number_input(
        "Semana", min_value=1, max_value=52, value=1, key="new_week"
    )
    new_category = st.selectbox("Categoría", CATEGORY_OPTIONS, key="new_cat")
    add = st.form_submit_button("Agregar")

    if add:
        if not new_title.strip():
            st.error("El título es obligatorio.")
        else:
            with Session(engine) as session:
                session.add(
                    TaskTemplateDB(
                        title=new_title.strip(),
                        description=new_description.strip() or None,
                        role=new_role,
                        week=int(new_week),
                        category=new_category,
                    )
                )
                session.commit()
            st.success("Template agregado.")
            st.rerun()
