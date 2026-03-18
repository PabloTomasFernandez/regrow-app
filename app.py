import json
import streamlit as st


# --- Funciones que ya escribiste ---


def guardar_proyectos(proyectos: list[dict], ruta: str = "proyectos.json") -> None:
    if proyectos:
        with open(ruta, "w") as archivo:
            json.dump(proyectos, archivo, indent=2)
    else:
        st.warning("No hay proyectos por guardar")


def cargar_proyectos(ruta: str = "proyectos.json") -> list[dict]:
    try:
        with open(ruta, "r") as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        return []


def buscar_tareas_por_persona(proyectos: list[dict], persona: str) -> list[dict]:
    tareas = []
    for proyecto in proyectos:
        for tarea in proyecto.get("tareas", []):
            if tarea["asignado_a"] == persona:
                tareas.append(
                    {
                        "empresa": proyecto["empresa"]["nombre"],
                        "tarea": tarea["nombre"],
                        "estado": tarea["estado"],
                        "fecha_vencimiento": tarea["fecha_vencimiento"],
                        "semana": tarea["semana"],
                    }
                )
    return tareas

def buscar_todas_tareas(proyectos: list[dict]) -> list[dict]:
    tareas = []
    for proyecto in proyectos:
        for tarea in proyecto.get("tareas", []):
            tareas.append(
                {
                    "empresa": proyecto["empresa"]["nombre"],
                    "tarea": tarea["nombre"],
                    "estado": tarea["estado"],
                    "fecha_vencimiento": tarea["fecha_vencimiento"],
                    "semana": tarea["semana"],
                }
            )
    return tareas

# --- Datos de ejemplo ---

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
        "activo": True,
        "started_date": "2026-03-19",
        "end_date": "",
        "equipo": {
            "pusher_coach": "clg@regrow.academy",
            "account_manager": "mb@regrow.agency",
            "copy": "dm@regrow.academy",
            "sdr": "ar@regrow.agency",
            "automater": "tf@regrow.agency",
            "coo": "fv@regrow.academy",
        },
        "tareas": [
            {
                "nombre": "Onboarding",
                "estado": "completado",
                "asignado_a": "clg@regrow.academy",
                "semana": 1,
                "fecha_vencimiento": "2026-03-26",
                "completado": True,
            },
            {
                "nombre": "Propuesta de secuencia de mensajes",
                "estado": "sin_iniciar",
                "asignado_a": "dm@regrow.academy",
                "semana": 4,
                "fecha_vencimiento": "2026-04-09",
                "completado": False,
            },
            {
                "nombre": "Prospección de leads",
                "estado": "sin_iniciar",
                "asignado_a": "ar@regrow.agency",
                "semana": 5,
                "fecha_vencimiento": "2026-04-16",
                "completado": False,
            },
            {
                "nombre": "Reunión Estrategia Comercial",
                "estado": "sin_iniciar",
                "asignado_a": "mb@regrow.agency",
                "semana": 3,
                "fecha_vencimiento": "2026-04-02",
                "completado": False,
            },
            {
                "nombre": "Automatización Conexiones Lemlist",
                "estado": "sin_iniciar",
                "asignado_a": "tf@regrow.agency",
                "semana": 5,
                "fecha_vencimiento": "2026-04-16",
                "completado": False,
            },
        ],
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
        "activo": False,
        "started_date": "2026-01-19",
        "end_date": "2026-03-19",
        "equipo": {
            "pusher_coach": "clg@regrow.academy",
            "account_manager": "rg@regrow.agency",
            "copy": "dm@regrow.academy",
            "sdr": "mg@regrow.agency",
            "automater": "tf@regrow.agency",
            "coo": "fv@regrow.academy",
        },
        "tareas": [
            {
                "nombre": "Onboarding",
                "estado": "completado",
                "asignado_a": "clg@regrow.academy",
                "semana": 1,
                "fecha_vencimiento": "2026-01-26",
                "completado": True,
            },
            {
                "nombre": "Propuesta de secuencia de mensajes",
                "estado": "completado",
                "asignado_a": "dm@regrow.academy",
                "semana": 4,
                "fecha_vencimiento": "2026-02-09",
                "completado": True,
            },
            {
                "nombre": "Prospección de leads",
                "estado": "completado",
                "asignado_a": "mg@regrow.agency",
                "semana": 5,
                "fecha_vencimiento": "2026-02-16",
                "completado": True,
            },
        ],
    },
    {
        "id": 3,
        "empresa": {"nombre": "CyberShield", "web": "www.cybershield.io"},
        "contacto": {
            "nombre": "Carlos",
            "apellido": "Méndez",
            "linkedin_url": "https://www.linkedin.com/in/cmendez-cs",
            "ghl_url": "https://app.gohighlevel.com/v2/location/cs_003",
        },
        "activo": True,
        "started_date": "2026-03-01",
        "end_date": "",
        "equipo": {
            "pusher_coach": "clg@regrow.academy",
            "account_manager": "mb@regrow.agency",
            "copy": "dm@regrow.academy",
            "sdr": "ar@regrow.agency",
            "automater": "tf@regrow.agency",
            "coo": "fv@regrow.academy",
        },
        "tareas": [
            {
                "nombre": "Onboarding",
                "estado": "completado",
                "asignado_a": "clg@regrow.academy",
                "semana": 1,
                "fecha_vencimiento": "2026-03-08",
                "completado": True,
            },
            {
                "nombre": "Auditoría de Perfiles LinkedIn",
                "estado": "completado",
                "asignado_a": "mb@regrow.agency",
                "semana": 2,
                "fecha_vencimiento": "2026-03-15",
                "completado": True,
            },
            {
                "nombre": "Redacción de Lead Magnet (Ebook)",
                "estado": "en_progreso",
                "asignado_a": "dm@regrow.academy",
                "semana": 3,
                "fecha_vencimiento": "2026-03-22",
                "completado": False,
            },
            {
                "nombre": "Configuración de CRM y Pipelines",
                "estado": "sin_iniciar",
                "asignado_a": "tf@regrow.agency",
                "semana": 4,
                "fecha_vencimiento": "2026-03-29",
                "completado": False,
            },
        ],
    },
]


# --- App de Streamlit ---

st.set_page_config(page_title="Regrow - Gestor de Proyectos", layout="wide")
st.title("Regrow - Gestor de proyectos")
st.caption("Panel interno del equipo")

# Cargar datos (o usar los de ejemplo si no hay archivo)
proyectos = cargar_proyectos()
if not proyectos:
    proyectos = PROYECTOS_EJEMPLO
    guardar_proyectos(proyectos)

# --- Sidebar: filtros ---
st.sidebar.header("Filtros")

filtro_estado = st.sidebar.selectbox(
    "Estado del proyecto",
    ["Todos", "Activos", "Inactivos"],
)

# Recolectar todos los emails del equipo
todos_los_emails = set()
for p in proyectos:
    for email in p["equipo"].values():
        todos_los_emails.add(email)

filtro_persona = st.sidebar.selectbox(
    "Miembro del equipo",
    ["Todos"] + sorted(todos_los_emails),
)

# --- Filtrar proyectos por estado ---
if filtro_estado == "Activos":
    proyectos_filtrados = [p for p in proyectos if p["activo"]]
elif filtro_estado == "Inactivos":
    proyectos_filtrados = [p for p in proyectos if not p["activo"]]
else:
    proyectos_filtrados = proyectos

# --- Métricas ---
activos = sum(1 for p in proyectos if p["activo"])
todas_tareas = []
for p in proyectos:
    todas_tareas.extend(p.get("tareas", []))
pendientes = sum(1 for t in todas_tareas if not t["completado"])
completadas = sum(1 for t in todas_tareas if t["completado"])

col1, col2, col3 = st.columns(3)
col1.metric("Proyectos activos", activos)
col2.metric("Tareas pendientes", pendientes)
col3.metric("Tareas completadas", completadas)

# --- Tabla de proyectos ---
st.subheader("Proyectos")

datos_tabla = []
for p in proyectos_filtrados:
    datos_tabla.append(
        {
            "Empresa": p["empresa"]["nombre"],
            "Contacto": f"{p['contacto']['nombre']} {p['contacto']['apellido']}",
            "Account Manager": p["equipo"]["account_manager"],
            "Estado": "Activo" if p["activo"] else "Inactivo",
        }
    )

if datos_tabla:
    st.dataframe(datos_tabla, use_container_width=True, hide_index=True)
else:
    st.info("No hay proyectos con ese filtro")

# --- Tareas por persona ---
if filtro_persona != "Todos":
    st.subheader(f"Tareas de {filtro_persona}")
    tareas = buscar_tareas_por_persona(proyectos, filtro_persona)
    if tareas:
        st.dataframe(tareas, use_container_width=True, hide_index=True)
    else:
        st.info(f"No hay tareas asignadas a {filtro_persona}")
else:
    st.subheader(f"Tareas de {filtro_persona}")
    tareas = buscar_todas_tareas(proyectos)
    if tareas:
        st.dataframe(tareas, use_container_width=True, hide_index=True)
    else:
        st.info(f"No hay tareas asignadas a {filtro_persona}")