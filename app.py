import streamlit as st

from funciones import cargar_proyectos, guardar_proyectos

PROYECTOS_EJEMPLO = [
    {
        "id": 1,
        "empresa": {"nombre": "Roisense", "web": "www.roisense.com"},
        "contacto": {
            "nombre": "Jose",
            "apellido": "Perez",
            "linkedin_url": "...",
            "ghl_url": "...",
        },
        "estado": "inactivo",
        "started_date": "",
        "end_date": "",
        "equipo": {
            "pusher_coach": "clg@regrow.academy",
            "account_manager": "mb@regrow.agency",
            "copy": "dm@regrow.academy",
            "sdr": "ar@regrow.agency",
            "automater": "tf@regrow.agency",
            "coo": "fv@regrow.academy",
        },
        "tareas": [],
        "notas": [],
    },
    {
        "id": 2,
        "empresa": {"nombre": "Make", "web": "www.make.com"},
        "contacto": {
            "nombre": "Maria",
            "apellido": "Perez",
            "linkedin_url": "...",
            "ghl_url": "...",
        },
        "estado": "pausado",
        "started_date": "2026-01-19",
        "end_date": "",
        "equipo": {
            "pusher_coach": "clg@regrow.academy",
            "account_manager": "rg@regrow.agency",
            "copy": "dm@regrow.academy",
            "sdr": "mg@regrow.agency",
            "automater": "tf@regrow.agency",
            "coo": "fv@regrow.academy",
        },
        "tareas": [],
        "notas": [
            {
                "autor": "clg@regrow.academy",
                "fecha": "2026-03-15",
                "texto": "Cliente no realizó el pago. Pausar tareas.",
            }
        ],
    },
]

st.set_page_config(page_title="Regrow - Gestor de Proyectos", layout="wide")
st.title("Regrow - Gestor de proyectos")
st.caption("Panel interno del equipo")

# Cargar datos
proyectos = cargar_proyectos()
if not proyectos:
    proyectos = PROYECTOS_EJEMPLO
    guardar_proyectos(proyectos)

# --- Métricas ---
activos = sum(1 for p in proyectos if p["estado"] == "activo")
pausados = sum(1 for p in proyectos if p["estado"] == "pausado")
inactivos = sum(1 for p in proyectos if p["estado"] == "inactivo")
todas_tareas = []
for p in proyectos:
    todas_tareas.extend(p.get("tareas", []))
pendientes = sum(1 for t in todas_tareas if t["estado"] != "completado")
completadas = sum(1 for t in todas_tareas if t["estado"] == "completado")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Activos", activos)
col2.metric("Pausados", pausados)
col3.metric("Inactivos", inactivos)
col4.metric("Tareas pendientes", pendientes)
col5.metric("Tareas completadas", completadas)

# --- Resumen rápido ---
st.subheader("Resumen de proyectos")

datos_tabla = []
for p in proyectos:
    num_tareas = len(p.get("tareas", []))
    tareas_completadas = sum(
        1 for t in p.get("tareas", []) if t["estado"] == "completado"
    )
    datos_tabla.append(
        {
            "Empresa": p["empresa"]["nombre"],
            "Contacto": f"{p['contacto']['nombre']} {p['contacto']['apellido']}",
            "Estado": p["estado"].capitalize(),
            "Tareas": f"{tareas_completadas}/{num_tareas}",
            "Inicio": p.get("started_date", ""),
        }
    )

if datos_tabla:
    st.dataframe(datos_tabla, use_container_width=True, hide_index=True)

st.info("Usá el menú de la izquierda para navegar entre secciones")
