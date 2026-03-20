import json
from datetime import datetime, timedelta

from templates import (
    CAMPANAS_INICIALES,
    TEMPLATE_BASE,
    TEMPLATES_CAMPANA,
)

# --- Funciones de fechas ---


def calcular_fecha_vencimiento(fecha_onboarding: str, semana: int) -> str:
    """Calcula la fecha de vencimiento según onboarding y semana."""
    inicio = datetime.strptime(fecha_onboarding, "%Y-%m-%d")
    dias_hasta_viernes = (4 - inicio.weekday()) % 7
    fecha = inicio + timedelta(days=7 * (semana - 1) + dias_hasta_viernes)
    return fecha.strftime("%Y-%m-%d")


def proximo_viernes(fecha: datetime) -> datetime:
    dias_hasta_viernes = (4 - fecha.weekday()) % 7
    return fecha + timedelta(days=dias_hasta_viernes)


# --- Funciones de persistencia ---


def guardar_proyectos(proyectos: list[dict], ruta: str = "proyectos.json") -> bool:
    if not proyectos:
        return False
    with open(ruta, "w") as archivo:
        json.dump(proyectos, archivo, indent=2, ensure_ascii=False)
    return True


def cargar_proyectos(ruta: str = "proyectos.json") -> list[dict]:
    try:
        with open(ruta) as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        return []


# --- Funciones de tareas ---


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


def cambiar_estado_tarea(
    proyectos: list[dict],
    proyecto_id: int,
    nombre_tarea: str,
    nuevo_estado: str,
    comentario: str = "",
    autor: str = "",
    fecha_realizado: str = "",
) -> bool:
    for proyecto in proyectos:
        if proyecto["id"] == proyecto_id:
            for tarea in proyecto["tareas"]:
                if tarea["nombre"] == nombre_tarea:
                    tarea["estado"] = nuevo_estado
                    if nuevo_estado == "completado":
                        tarea["fecha_realizado"] = (
                            fecha_realizado or datetime.now().strftime("%Y-%m-%d")
                        )
                    if comentario:
                        tarea["comentarios"].append(
                            {
                                "autor": autor,
                                "fecha": datetime.now().strftime("%Y-%m-%d"),
                                "texto": comentario,
                            }
                        )
                    guardar_proyectos(proyectos)
                    return True
    return False


# --- Funciones de campañas ---


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


# --- Funciones de proyectos ---


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
        "empresa": {
            "nombre": empresa_nombre.strip(),
            "web": empresa_web.strip().lower(),
        },
        "contacto": {
            "nombre": contacto_nombre.strip(),
            "apellido": contacto_apellido.strip(),
            "linkedin_url": linkedin_url.strip(),
            "ghl_url": ghl_url.strip(),
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

    # Marcar Onboarding COO con la fecha real
    for tarea in tareas:
        if tarea["nombre"] == "Onboarding COO":
            tarea["fecha_vencimiento"] = fecha_inicio
            tarea["fecha_realizado"] = fecha_inicio
            tarea["estado"] = "completado"
            break

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
        {
            "nombre": "Aviso 1 mes para que finalice el proyecto",
            "semana": duracion_semanas - 5,
        },
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


def asignar_equipo(
    proyectos: list[dict],
    proyecto_id: int,
    equipo: dict,
) -> bool:
    for proyecto in proyectos:
        if proyecto["id"] == proyecto_id:
            proyecto["equipo"].update(equipo)
            guardar_proyectos(proyectos)
            return True
    return False


def agregar_sales_pilot(
    proyecto: dict,
    numero_campana: int,
    semana_inicio: int,
    fecha_inicio_proyecto: str = "",
) -> list[dict]:
    plantilla = TEMPLATES_CAMPANA["sales_pilot"]
    tareas = []
    for tarea in plantilla:
        email = proyecto["equipo"].get(tarea["rol"], "")
        semana = semana_inicio + tarea["offset"]
        fecha = ""
        if fecha_inicio_proyecto:
            fecha = calcular_fecha_vencimiento(fecha_inicio_proyecto, semana)
        tareas.append(
            crear_tarea(
                f"{tarea['nombre']} - Campaña {numero_campana}",
                email,
                semana,
                fecha,
            )
        )
    return tareas
    # 2. Generar las tareas con "- Campaña {numero_campana}" en el nombre
    # 3. Devolver la lista
