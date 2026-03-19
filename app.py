import json
from datetime import datetime, timedelta

import streamlit as st


# --- Templates ---

TEMPLATE_BASE = [
    # Semana 1 - Onboarding
    {"nombre": "Onboarding Pusher Coach", "rol": "pusher_coach", "semana": 1},
    {"nombre": "Envío de mensaje post onboarding (Pusher Coach)", "rol": "pusher_coach", "semana": 1},
    {"nombre": "Onboarding COO", "rol": "coo", "semana": 1},
    {"nombre": "Envío de mensaje post onboarding (COO)", "rol": "coo", "semana": 1},
    {"nombre": "Creación grupo Whatsapp/Slack", "rol": "account_manager", "semana": 1},
    {"nombre": "Agendamiento de llamadas", "rol": "coo", "semana": 1},
    # Semana 2 - Altas y credenciales
    {"nombre": "Alta SN", "rol": "coo", "semana": 2},
    {"nombre": "Credenciales LinkedIn", "rol": "coo", "semana": 2},
    {"nombre": "Alta Lemlist", "rol": "coo", "semana": 2},
    {"nombre": "Credenciales Lemlist", "rol": "coo", "semana": 2},
    {"nombre": "Entrevista de contenido", "rol": "copy", "semana": 2},
    {"nombre": "Lista de ampliación de red", "rol": "automater", "semana": 2},
    {"nombre": "Comienzo ampliación de red", "rol": "automater", "semana": 2},
    # Semana 3 - Propuestas y setup
    {"nombre": "Propuesta de mejora de perfil", "rol": "copy", "semana": 3},
    {"nombre": "Propuesta de ideas para posteos", "rol": "copy", "semana": 3},
    {"nombre": "Reunión estrategia comercial", "rol": "account_manager", "semana": 3},
    {"nombre": "Envío informe matriz de prospección", "rol": "account_manager", "semana": 3},
    {"nombre": "Reunión de automatizaciones", "rol": "automater", "semana": 3},
    {"nombre": "Lemlist pago", "rol": "automater", "semana": 3},
    {"nombre": "Conexión email a Lemlist", "rol": "automater", "semana": 3},
    {"nombre": "Armado búsqueda para FCA", "rol": "sdr", "semana": 3},
    {"nombre": "Envío csv para FCA", "rol": "automater", "semana": 3},
    {"nombre": "Limpieza csv para FCA", "rol": "automater", "semana": 3},
    # Semana 4 - Validaciones e implementación
    {"nombre": "Validación de mejora de perfil", "rol": "copy", "semana": 4},
    {"nombre": "Implementación de mejora de perfil", "rol": "sdr", "semana": 4},
    {"nombre": "Validación de ideas para posteos", "rol": "copy", "semana": 4},
    {"nombre": "Propuesta de posteos", "rol": "copy", "semana": 4},
    {"nombre": "Integración Lemlist-CRM", "rol": "automater", "semana": 4},
    {"nombre": "Integración Lemlist-OpenAI", "rol": "automater", "semana": 4},
    {"nombre": "Integración Lemlist-Looker", "rol": "automater", "semana": 4},
    {"nombre": "Armado blacklist", "rol": "sdr", "semana": 4},
    # Semana 5 - Posteos
    {"nombre": "Validación de posteos", "rol": "copy", "semana": 5},
    {"nombre": "Lanzamiento posteo 1", "rol": "sdr", "semana": 5},
    # Semana 6-8 - Posteos restantes
    {"nombre": "Lanzamiento posteo 2", "rol": "sdr", "semana": 6},
    {"nombre": "Lanzamiento posteo 3", "rol": "sdr", "semana": 7},
    {"nombre": "Lanzamiento posteo 4", "rol": "sdr", "semana": 8},
    # Semana 7 - Encuesta
    {"nombre": "Envío de encuesta de satisfacción", "rol": "pusher_coach", "semana": 7},
]

TEMPLATES_CAMPANA = {
    "campana_normal": [
        {"nombre": "Propuesta de prospecting canvas", "rol": "account_manager", "offset": 0},
        {"nombre": "Validación de prospecting canvas", "rol": "account_manager", "offset": 1},
        {"nombre": "Propuesta de prospección de cuentas", "rol": "sdr", "offset": 1},
        {"nombre": "Validación de prospección de cuentas", "rol": "account_manager", "offset": 1},
        {"nombre": "Propuesta de secuencia de mensajes", "rol": "copy", "offset": 1},
        {"nombre": "Prospección de leads", "rol": "sdr", "offset": 2},
        {"nombre": "Validación de secuencia de mensajes", "rol": "copy", "offset": 2},
        {"nombre": "Automatización conexiones Lemlist", "rol": "automater", "offset": 2},
        {"nombre": "Automatización mensajes Lemlist", "rol": "automater", "offset": 3},
        {"nombre": "Informe de resultados", "rol": "account_manager", "offset": 4},
    ],
    "sales_pilot": [
        {"nombre": "Prospección de cuentas SP", "rol": "sdr", "offset": 1},
        {"nombre": "Cargar a Lemlist SP", "rol": "sdr", "offset": 2},
        {"nombre": "Automatización Lemlist SP", "rol": "automater", "offset": 2},
        {"nombre": "Informe de resultados SP", "rol": "account_manager", "offset": 4},
    ],
    "evento": [
        {"nombre": "Propuesta de prospección de cuentas", "rol": "sdr", "offset": 0},
        {"nombre": "Validación de prospección de cuentas", "rol": "account_manager", "offset": 1},
        {"nombre": "Prospección de leads", "rol": "sdr", "offset": 1},
        {"nombre": "Propuesta de secuencia de mensajes", "rol": "copy", "offset": 1},
        {"nombre": "Validación de secuencia de mensajes", "rol": "copy", "offset": 2},
        {"nombre": "Automatización conexiones Lemlist", "rol": "automater", "offset": 2},
        {"nombre": "Automatización mensajes Lemlist", "rol": "automater", "offset": 3},
        {"nombre": "Informe de resultados", "rol": "account_manager", "offset": 4},
    ],
}

CAMPANAS_INICIALES = [3, 7, 11]


# --- Funciones de fechas ---


def calcular_fecha_vencimiento(fecha_onboarding: str, semana: int) -> str:
    """Replica la fórmula del Excel: $G$4 + 7*(semana-1) + (5 - WEEKDAY($G$4, 2))"""
    inicio = datetime.strptime(fecha_onboarding, "%Y-%m-%d")
    dias_hasta_viernes = (4 - inicio.weekday()) % 7
    fecha = inicio + timedelta(days=7 * (semana - 1) + dias_hasta_viernes)
    return fecha.strftime("%Y-%m-%d")


def proximo_viernes(fecha: datetime) -> datetime:
    dias_hasta_viernes = (4 - fecha.weekday()) % 7
    if dias_hasta_viernes == 0 and fecha.weekday() != 4:
        dias_hasta_viernes = 7
    return fecha + timedelta(days=dias_hasta_viernes)


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
    proyectos: list[dict], personas: list[str] = None
) -> list[dict]:
    tareas = []
    for proyecto in proyectos:
        for tarea in proyecto.get("tareas", []):
            if not personas or tarea["asignado_a"] in personas:
                tareas.append(
                    {
                        "empresa": proyecto["empresa"]["nombre"],
                        "tarea": tarea["nombre"],
                        "estado": tarea["estado"],
                        "semana": tarea.get("semana", ""),
                        "fecha_vencimiento": tarea.get("fecha_vencimiento", ""),
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


def crear_tarea(nombre: str, email: str, semana: int, fecha: str) -> dict:
    """Crea un diccionario de tarea con todos los campos estándar."""
    return {
        "nombre": nombre,
        "asignado_a": email,
        "estado": "sin_iniciar",
        "semana": semana,
        "fecha_vencimiento": fecha,
        "fecha_realizado": "",
        "comentarios": [],
    }


def generar_tareas_campana(
    proyecto: dict,
    tipo: str,
    numero: int,
    semana_inicio: int,
    fecha_inicio_proyecto: str = "",
    incluir_sales_pilot: bool = False,
) -> list[dict]:
    plantillas = TEMPLATES_CAMPANA[tipo]

    if tipo == "campana_normal" and incluir_sales_pilot:
        plantillas = plantillas + TEMPLATES_CAMPANA["sales_pilot"]

    etiqueta = "Evento" if tipo == "evento" else "Campaña"

    tareas = []
    for tarea in plantillas:
        email = proyecto["equipo"].get(tarea["rol"], "")
        semana = semana_inicio + tarea["offset"]
        fecha = ""
        if fecha_inicio_proyecto:
            fecha = calcular_fecha_vencimiento(fecha_inicio_proyecto, semana)
        tareas.append(
            crear_tarea(
                f"{tarea['nombre']} - {etiqueta} {numero}",
                email,
                semana,
                fecha,
            )
        )
    return tareas


def contar_campanas(proyecto: dict, tipo: str) -> int:
    etiqueta = "Evento" if tipo == "evento" else "Campaña"
    numeros = set()
    for tarea in proyecto.get("tareas", []):
        nombre = tarea["nombre"]
        if f"- {etiqueta} " in nombre:
            try:
                num = int(nombre.split(f"{etiqueta} ")[-1])
                numeros.add(num)
            except ValueError:
                pass
    return len(numeros)


def activar_proyecto(
    proyecto: dict,
    proyectos: list[dict],
    fecha_inicio: str,
    duracion_semanas: int = 14,
) -> None:
    proyecto["estado"] = "activo"
    proyecto["started_date"] = fecha_inicio
    tareas = []

    # 1. Tareas base
    for tarea in TEMPLATE_BASE:
        email = proyecto["equipo"].get(tarea["rol"], "")
        fecha = calcular_fecha_vencimiento(fecha_inicio, tarea["semana"])
        tareas.append(crear_tarea(tarea["nombre"], email, tarea["semana"], fecha))

    # 2. Tres campañas normales (semanas 3, 7, 11)
    for i, semana_inicio in enumerate(CAMPANAS_INICIALES):
        numero = i + 1
        tareas.extend(
            generar_tareas_campana(
                proyecto, "campana_normal", numero, semana_inicio, fecha_inicio
            )
        )

    # 3. Chequeos dinámicos
    num_chequeos = (duracion_semanas - 3) // 2 + 1
    for num_chequeo in range(1, num_chequeos):
        semana = (num_chequeo * 2) + 1
        if semana <= duracion_semanas:
            fecha = calcular_fecha_vencimiento(fecha_inicio, semana)
            tareas.append(
                crear_tarea(
                    f"Chequeo {num_chequeo} (WU, FU, ADS, CLASES)",
                    proyecto["equipo"].get("account_manager", ""),
                    semana,
                    fecha,
                )
            )

    # 4. Tareas de cierre
    tareas_cierre = [
        {"nombre": "Aviso 1 mes para que finalice el proyecto", "semana": duracion_semanas - 5},
        {"nombre": "Informe cierre interno", "semana": duracion_semanas},
        {"nombre": "Informe cierre cliente", "semana": duracion_semanas},
    ]
    for tc in tareas_cierre:
        fecha = calcular_fecha_vencimiento(fecha_inicio, tc["semana"])
        tareas.append(
            crear_tarea(
                tc["nombre"],
                proyecto["equipo"].get("account_manager", ""),
                tc["semana"],
                fecha,
            )
        )

    proyecto["tareas"].extend(tareas)
    guardar_proyectos(proyectos)


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


# --- App de Streamlit ---

st.set_page_config(page_title="Regrow - Gestor de Proyectos", layout="wide")
st.title("Regrow - Gestor de proyectos")
st.caption("Panel interno del equipo")

# Cargar datos
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

todos_los_emails = set()
for p in proyectos:
    for email in p["equipo"].values():
        if email:
            todos_los_emails.add(email)

filtro_persona = st.sidebar.multiselect(
    "Miembros del equipo",
    sorted(todos_los_emails),
    default=[],
    placeholder="Todos",
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

# --- Tabla de proyectos ---
st.subheader("Proyectos")

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
            "Fecha del Onboarding (referencia para todas las fechas)",
            value=proximo_viernes(datetime.now()),
            help="Fecha del Onboarding Fran. Las fechas de vencimiento se calculan con el viernes de cada semana.",
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
                    f"{proyecto['empresa']['nombre']} activado con {num_tareas} tareas. "
                    f"Inicio: {fecha_str}"
                )
                st.rerun()

# --- Tareas por persona ---
st.subheader(
    f"Tareas - {', '.join(filtro_persona) if filtro_persona else 'Todos'}"
)
tareas = buscar_tareas_por_persona(
    proyectos, filtro_persona if filtro_persona else None
)
if tareas:
    st.dataframe(tareas, use_container_width=True, hide_index=True)
else:
    st.info("No hay tareas asignadas")

# --- Agregar campaña a un proyecto ---
proyectos_activos = [p for p in proyectos if p["estado"] == "activo"]

if proyectos_activos:
    st.subheader("Agregar campaña")

    nombres_activos = [
        f"{p['empresa']['nombre']} (ID: {p['id']})" for p in proyectos_activos
    ]

    with st.form("nueva_campana", clear_on_submit=True):
        proyecto_seleccionado = st.selectbox("Proyecto", nombres_activos)

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