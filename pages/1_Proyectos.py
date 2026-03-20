from datetime import datetime

import streamlit as st

from funciones import (
    activar_proyecto,
    cargar_proyectos,
    proximo_viernes,
)

st.set_page_config(page_title="Proyectos - Regrow", layout="wide")
st.title("Proyectos")

proyectos = cargar_proyectos()

# --- Filtros ---
filtro_estado = st.selectbox(
    "Filtrar por estado",
    ["Todos", "Activo", "Inactivo", "Pausado"],
)

if filtro_estado == "Todos":
    proyectos_filtrados = proyectos
else:
    proyectos_filtrados = [p for p in proyectos if p["estado"] == filtro_estado.lower()]

# --- Tabla de proyectos ---
datos_tabla = []
for p in proyectos_filtrados:
    num_tareas = len(p.get("tareas", []))
    datos_tabla.append(
        {
            "Empresa": p["empresa"]["nombre"],
            "Contacto": f"{p['contacto']['nombre']} {p['contacto']['apellido']}",
            "AM": p["equipo"]["account_manager"] or "Sin asignar",
            "Estado": p["estado"].capitalize(),
            "Tareas": num_tareas,
            "Inicio": p.get("started_date", ""),
            "Última nota": p["notas"][-1]["texto"] if p["notas"] else "",
        }
    )

if datos_tabla:
    st.dataframe(datos_tabla, use_container_width=True, hide_index=True)
else:
    st.info("No hay proyectos con ese filtro")

# --- Activar proyecto ---
proyectos_inactivos = [p for p in proyectos if p["estado"] == "inactivo"]

if proyectos_inactivos:
    st.subheader("Activar proyecto")

    nombres_inactivos = [
        f"{p['empresa']['nombre']} (ID: {p['id']})" for p in proyectos_inactivos
    ]

    with st.form("activar_proyecto", clear_on_submit=True):
        proyecto_seleccionado = st.selectbox("Proyecto a activar", nombres_inactivos)
        fecha_inicio_input = st.date_input(
            "Fecha del Onboarding COO",
            value=proximo_viernes(datetime.now()),
            help="Todas las fechas de vencimiento se calculan a partir de esta fecha",
        )
        duracion = st.number_input(
            "Duración del proyecto (semanas)", min_value=4, max_value=52, value=14
        )
        activar = st.form_submit_button("Activar y generar tareas")

        if activar:
            idx = nombres_inactivos.index(proyecto_seleccionado)
            proyecto = proyectos_inactivos[idx]

            roles_vacios = [
                rol for rol, email in proyecto["equipo"].items() if not email
            ]
            if roles_vacios:
                st.error(
                    f"Asigná el equipo antes de activar. "
                    f"Falta: {', '.join(roles_vacios)}"
                )
            else:
                fecha_str = fecha_inicio_input.strftime("%Y-%m-%d")
                activar_proyecto(proyecto, proyectos, fecha_str, duracion)
                num_tareas = len(proyecto["tareas"])
                st.success(
                    f"{proyecto['empresa']['nombre']} activado "
                    f"con {num_tareas} tareas. Inicio: {fecha_str}"
                )
