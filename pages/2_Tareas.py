from datetime import datetime

import streamlit as st

from funciones import (
    buscar_tareas_por_persona,
    cambiar_estado_tarea,
    cargar_proyectos,
)

st.set_page_config(page_title="Tareas - Regrow", layout="wide")
st.title("Tareas")

proyectos = cargar_proyectos()

# --- Filtro por persona ---
todos_los_emails = set()
for p in proyectos:
    for email in p["equipo"].values():
        if email:
            todos_los_emails.add(email)

filtro_persona = st.multiselect(
    "Filtrar por miembro del equipo",
    sorted(todos_los_emails),
    default=[],
    placeholder="Todos",
)

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

        # Ver comentarios
        nombres_tareas = [t["nombre"] for t in tareas_proyecto]
        tarea_sel_ver = st.selectbox(
            "Ver comentarios de tarea", nombres_tareas, key="ver_tarea"
        )

        tarea_encontrada = None
        for t in tareas_proyecto:
            if t["nombre"] == tarea_sel_ver:
                tarea_encontrada = t
                break

        if tarea_encontrada:
            with st.expander("Comentarios"):
                if tarea_encontrada["comentarios"]:
                    for c in tarea_encontrada["comentarios"]:
                        st.write(f"**{c['autor']}** ({c['fecha']}): {c['texto']}")
                else:
                    st.info("Sin comentarios")

        # Cambiar estado
        with st.form("cambiar_estado", clear_on_submit=True):
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