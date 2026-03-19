from datetime import datetime

import streamlit as st

from funciones import (
    activar_proyecto,
    asignar_equipo,
    buscar_tareas_por_persona,
    cambiar_estado_tarea,
    cargar_proyectos,
    contar_campanas,
    crear_proyecto,
    generar_tareas_campana,
    guardar_proyectos,
    proximo_viernes,
)

ROLES = ["pusher_coach", "account_manager", "copy", "sdr", "automater", "coo"]

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


# --- App ---

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
            pusher_coach = st.text_input("Pusher Coach", value=equipo_actual.get("pusher_coach", ""))
            account_manager = st.text_input("Account Manager", value=equipo_actual.get("account_manager", ""))
            copy = st.text_input("Copy", value=equipo_actual.get("copy", ""))

        with col_der:
            sdr = st.text_input("SDR", value=equipo_actual.get("sdr", ""))
            automater = st.text_input("Automater", value=equipo_actual.get("automater", ""))
            coo = st.text_input("COO", value=equipo_actual.get("coo", ""))

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
            st.success(f"Equipo actualizado para {proyecto_equipo['empresa']['nombre']}")
            st.rerun()

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

# --- Gestión de tareas ---
proyectos_activos = [p for p in proyectos if p["estado"] == "activo"]

if proyectos_activos:
    st.subheader("Gestión de tareas")

    nombres_activos_tareas = [
        f"{p['empresa']['nombre']} (ID: {p['id']})" for p in proyectos_activos
    ]
    proyecto_sel = st.selectbox(
        "Proyecto", nombres_activos_tareas, key="sel_tareas"
    )
    idx = nombres_activos_tareas.index(proyecto_sel)
    proyecto_actual = proyectos_activos[idx]

    tareas_proyecto = proyecto_actual.get("tareas", [])
    if tareas_proyecto:
        datos_tareas = []
        for t in tareas_proyecto:
            datos_tareas.append(
                {
                    "Tarea": t["nombre"],
                    "Asignado": t["asignado_a"],
                    "Estado": t["estado"],
                    "Semana": t.get("semana", ""),
                    "Vence": t.get("fecha_vencimiento", ""),
                    "Realizado": t.get("fecha_realizado", ""),
                }
            )
        st.dataframe(datos_tareas, use_container_width=True, hide_index=True)

        with st.form("cambiar_estado", clear_on_submit=True):
            nombres_tareas = [t["nombre"] for t in tareas_proyecto]
            tarea_sel = st.selectbox("Tarea", nombres_tareas)
            nuevo_estado = st.selectbox(
                "Nuevo estado",
                ["sin_iniciar", "en_curso", "completado"],
            )
            fecha_realizado_input = st.date_input(
                "Fecha de realización (solo aplica si es completado)",
                value=datetime.now(),
            )
            comentario = st.text_input("Comentario (opcional)")

            cambiar = st.form_submit_button("Actualizar tarea")

            if cambiar:
                fecha_str = ""
                if nuevo_estado == "completado":
                    fecha_str = fecha_realizado_input.strftime("%Y-%m-%d")
                exito = cambiar_estado_tarea(
                    proyectos=proyectos,
                    proyecto_id=proyecto_actual["id"],
                    nombre_tarea=tarea_sel,
                    nuevo_estado=nuevo_estado,
                    comentario=comentario,
                    autor="admin",
                    fecha_realizado=fecha_str,
                )
                if exito:
                    st.success(f"Tarea actualizada a: {nuevo_estado}")
                    st.rerun()
                else:
                    st.error("No se encontró la tarea")
    else:
        st.info("Este proyecto no tiene tareas")

# --- Agregar campaña a un proyecto ---
if proyectos_activos:
    st.subheader("Agregar campaña")

    nombres_activos = [
        f"{p['empresa']['nombre']} (ID: {p['id']})" for p in proyectos_activos
    ]

    with st.form("nueva_campana", clear_on_submit=True):
        proyecto_seleccionado = st.selectbox(
            "Proyecto", nombres_activos, key="sel_campana"
        )

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