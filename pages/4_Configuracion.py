import streamlit as st

from funciones import (
    asignar_equipo,
    cargar_proyectos,
    crear_proyecto,
)

st.set_page_config(page_title="Configuración - Regrow", layout="wide")
st.title("Configuración")

proyectos = cargar_proyectos()

# --- Asignar equipo ---
proyectos_sin_equipo = [
    p for p in proyectos
    if p["estado"] in ("inactivo", "activo")
    and any(not email for email in p["equipo"].values())
]

if proyectos_sin_equipo:
    st.subheader("Asignar equipo")

    nombres_sin_equipo = [
        f"{p['empresa']['nombre']} (ID: {p['id']})" for p in proyectos_sin_equipo
    ]

    proyecto_equipo_sel = st.selectbox(
        "Proyecto", nombres_sin_equipo, key="sel_equipo"
    )
    idx = nombres_sin_equipo.index(proyecto_equipo_sel)
    proyecto_equipo = proyectos_sin_equipo[idx]

    with st.form("asignar_equipo", clear_on_submit=False):
        equipo_actual = proyecto_equipo["equipo"]
        col_izq, col_der = st.columns(2)

        with col_izq:
            pusher_coach = st.text_input(
                "Pusher Coach", value=equipo_actual.get("pusher_coach", "")
            )
            account_manager = st.text_input(
                "Account Manager", value=equipo_actual.get("account_manager", "")
            )
            copy = st.text_input(
                "Copy", value=equipo_actual.get("copy", "")
            )

        with col_der:
            sdr = st.text_input(
                "SDR", value=equipo_actual.get("sdr", "")
            )
            automater = st.text_input(
                "Automater", value=equipo_actual.get("automater", "")
            )
            coo = st.text_input(
                "COO", value=equipo_actual.get("coo", "")
            )

        guardar_equipo = st.form_submit_button("Guardar equipo")

        if guardar_equipo:
            nuevo_equipo = {
                "pusher_coach": pusher_coach,
                "account_manager": account_manager,
                "copy": copy,
                "sdr": sdr,
                "automater": automater,
                "coo": coo,
            }
            asignar_equipo(proyectos, proyecto_equipo["id"], nuevo_equipo)
            st.success(
                f"Equipo actualizado para {proyecto_equipo['empresa']['nombre']}"
            )
            st.rerun()

# --- Crear proyecto ---
st.subheader("Crear nuevo proyecto")

with st.form("nuevo_proyecto", clear_on_submit=True):
    col_izq, col_der = st.columns(2)

    with col_izq:
        empresa_nombre = st.text_input("Nombre de la empresa *")
        contacto_nombre = st.text_input("Nombre del contacto *")
        linkedin_url = st.text_input("LinkedIn URL")

    with col_der:
        empresa_web = st.text_input("Web de la empresa *")
        contacto_apellido = st.text_input("Apellido del contacto *")
        ghl_url = st.text_input("GHL URL")

    enviado_proyecto = st.form_submit_button("Crear proyecto")

    if enviado_proyecto:
        if not all([empresa_nombre, empresa_web, contacto_nombre, contacto_apellido]):
            st.error("Completá todos los campos obligatorios (*)")
        else:
            nuevo = crear_proyecto(
                proyectos=proyectos,
                empresa_nombre=empresa_nombre,
                empresa_web=empresa_web,
                contacto_nombre=contacto_nombre,
                contacto_apellido=contacto_apellido,
                linkedin_url=linkedin_url,
                ghl_url=ghl_url,
            )
            st.success(
                f"Proyecto creado: {nuevo['empresa']['nombre']} (ID: {nuevo['id']})"
            )
            st.rerun()