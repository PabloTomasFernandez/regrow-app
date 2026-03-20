import streamlit as st

from funciones import (
    agregar_sales_pilot,
    cargar_proyectos,
    contar_campanas,
    generar_tareas_campana,
    guardar_proyectos,
)

st.set_page_config(page_title="Campañas - Regrow", layout="wide")
st.title("Campañas")

proyectos = cargar_proyectos()
proyectos_activos = [p for p in proyectos if p["estado"] == "activo"]

if not proyectos_activos:
    st.info("No hay proyectos activos para agregar campañas")
    st.stop()

# --- Agregar campaña ---
st.subheader("Agregar campaña")

nombres_activos = [
    f"{p['empresa']['nombre']} (ID: {p['id']})" for p in proyectos_activos
]

with st.form("nueva_campana", clear_on_submit=True):
    proyecto_seleccionado = st.selectbox("Proyecto", nombres_activos, key="sel_campana")

    tipo_campana = st.selectbox(
        "Tipo de campaña",
        ["Campaña normal", "Evento"],
    )

    semana_inicio = st.number_input(
        "Semana de inicio de la campaña",
        min_value=1,
        max_value=52,
        value=12,
        help="Semana del proyecto en la que arranca esta campaña",
    )

    incluir_sp = False
    if tipo_campana == "Campaña normal":
        incluir_sp = st.checkbox("Incluir Sales Pilot")

    enviado = st.form_submit_button("Generar tareas")

    if enviado:
        idx = nombres_activos.index(proyecto_seleccionado)
        proyecto = proyectos_activos[idx]
        tipo = "campana_normal" if tipo_campana == "Campaña normal" else "evento"
        numero = contar_campanas(proyecto, tipo) + 1

        fecha_inicio_proy = proyecto.get("started_date", "")

        nuevas_tareas = generar_tareas_campana(
            proyecto, tipo, numero, semana_inicio, fecha_inicio_proy, incluir_sp
        )

        for p in proyectos:
            if p["id"] == proyecto["id"]:
                p["tareas"].extend(nuevas_tareas)
                break

        guardar_proyectos(proyectos)
        etiqueta = "Evento" if tipo == "evento" else "Campaña"
        st.success(
            f"{etiqueta} {numero} generada para "
            f"{proyecto['empresa']['nombre']} "
            f"({len(nuevas_tareas)} tareas, desde semana {semana_inicio})"
        )
        st.rerun()

# --- Agregar Sales Pilot ---
st.subheader("Agregar Sales Pilot a campaña existente")

proyecto_sp_sel = st.selectbox("Proyecto", nombres_activos, key="sel_sp_proyecto")
idx = nombres_activos.index(proyecto_sp_sel)
proyecto_sp = proyectos_activos[idx]

num_campanas = contar_campanas(proyecto_sp, "campana_normal")

if num_campanas > 0:
    with st.form("agregar_sp", clear_on_submit=True):
        campana_sel = st.selectbox(
            "Campaña", list(range(1, num_campanas + 1)), key="sel_sp_campana"
        )
        semana_inicio_sp = st.number_input(
            "Semana de inicio del Sales Pilot",
            min_value=1,
            max_value=52,
            value=12,
        )
        enviado_sp = st.form_submit_button("Generar tareas SP")

        if enviado_sp:
            fecha_inicio_proy = proyecto_sp.get("started_date", "")
            nuevas_tareas = agregar_sales_pilot(
                proyecto_sp, campana_sel, semana_inicio_sp, fecha_inicio_proy
            )
            for p in proyectos:
                if p["id"] == proyecto_sp["id"]:
                    p["tareas"].extend(nuevas_tareas)
                    break
            guardar_proyectos(proyectos)
            st.success(
                f"Sales Pilot agregado a Campaña {campana_sel} "
                f"({len(nuevas_tareas)} tareas)"
            )
            st.rerun()
else:
    st.info("Este proyecto no tiene campañas todavía")
