import json

import streamlit as st


# --- Funciones de datos ---


def guardar_proyectos(proyectos: list[dict], ruta: str = "proyectos.json") -> None:
    if proyectos:
        with open(ruta, "w") as archivo:
            json.dump(proyectos, archivo, indent=2, ensure_ascii=False)
    else:
        st.warning("No hay proyectos por guardar")


def cargar_proyectos(ruta: str = "proyectos.json") -> list[dict]:
    try:
        with open(ruta, "r") as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        return []


def buscar_tareas_por_persona(
    proyectos: list[dict], persona: str = "Todos"
) -> list[dict]:
    tareas = []
    for proyecto in proyectos:
        for tarea in proyecto.get("tareas", []):
            if persona == "Todos" or tarea["asignado_a"] == persona:
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


def crear_proyecto(
    proyectos: list[dict],
    empresa_nombre: str,
    empresa_web: str,
    contacto_nombre: str,
    contacto_apellido: str,
    linkedin_url: str = "",
    ghl_url: str = "",
) -> dict:
    proyecto_id = max((p["id"] for p in proyectos), default=0) + 1
    new_project = {
        "id": proyecto_id,
        "empresa": {"nombre": empresa_nombre, "web": empresa_web},
        "contacto": {
            "nombre": contacto_nombre,
            "apellido": contacto_apellido,
            "linkedin_url": linkedin_url,
            "ghl_url": ghl_url,
        },
        "estado": "inactivo",
        "started_date": "",
        "end_date": "",
        "equipo": {
            "pusher_coach": "",
            "account_manager": "",
            "copy": "",
            "sdr": "",
            "automater": "",
            "coo": "",
        },
        "tareas": [],
        "notas": [],
    }
    proyectos.append(new_project)
    guardar_proyectos(proyectos)
    return new_project


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
        "estado": "activo",
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
        "notas": [
            {
                "autor": "clg@regrow.academy",
                "fecha": "2026-03-15",
                "texto": "Cliente no realizó el pago. Pausar tareas.",
            }
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
    ["Todos", "Activo", "Inactivo", "Pausado"],
)

# Recolectar todos los emails del equipo
todos_los_emails = set()
for p in proyectos:
    for email in p["equipo"].values():
        if email:
            todos_los_emails.add(email)

filtro_persona = st.sidebar.selectbox(
    "Miembro del equipo",
    ["Todos"] + sorted(todos_los_emails),
)

# --- Filtrar proyectos por estado ---
if filtro_estado == "Todos":
    proyectos_filtrados = proyectos
else:
    proyectos_filtrados = [
        p for p in proyectos if p["estado"] == filtro_estado.lower()
    ]

# --- Métricas ---
activos = sum(1 for p in proyectos if p["estado"] == "activo")
pausados = sum(1 for p in proyectos if p["estado"] == "pausado")
todas_tareas = []
for p in proyectos:
    todas_tareas.extend(p.get("tareas", []))
pendientes = sum(1 for t in todas_tareas if not t["completado"])
completadas = sum(1 for t in todas_tareas if t["completado"])

col1, col2, col3, col4 = st.columns(4)
col1.metric("Proyectos activos", activos)
col2.metric("Proyectos pausados", pausados)
col3.metric("Tareas pendientes", pendientes)
col4.metric("Tareas completadas", completadas)

# --- Tabla de proyectos ---
st.subheader("Proyectos")

datos_tabla = []
for p in proyectos_filtrados:
    datos_tabla.append(
        {
            "Empresa": p["empresa"]["nombre"],
            "Contacto": f"{p['contacto']['nombre']} {p['contacto']['apellido']}",
            "Account Manager": p["equipo"]["account_manager"] or "Sin asignar",
            "Estado": p["estado"].capitalize(),
            "Última nota": p["notas"][-1]["texto"] if p["notas"] else "Sin notas",
        }
    )

if datos_tabla:
    st.dataframe(datos_tabla, use_container_width=True, hide_index=True)
else:
    st.info("No hay proyectos con ese filtro")

# --- Tareas por persona ---
st.subheader(f"Tareas - {filtro_persona}")
tareas = buscar_tareas_por_persona(proyectos, filtro_persona)
if tareas:
    st.dataframe(tareas, use_container_width=True, hide_index=True)
else:
    st.info("No hay tareas asignadas")

# --- Formulario para crear proyecto ---
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

    enviado = st.form_submit_button("Crear proyecto")

    if enviado:
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