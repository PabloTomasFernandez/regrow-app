from sqlmodel import Session, select
from database import engine
from templates import TEMPLATE_BASE, CAMPANAS_INICIALES, TEMPLATES_CAMPANA
from db_modelos import (
    Asignacion,
    Contacto,
    Empresa,
    Miembro,
    Nota,
    Proyecto,
    Puesto,
    Tarea,
)
from funciones import calcular_fecha_vencimiento


def listar_proyectos() -> list[Proyecto]:
    with Session(engine) as session:
        proyectos = session.exec(select(Proyecto)).all()
        return proyectos


def crear_proyecto_db(
    empresa_nombre: str,
    empresa_web: str,
    contacto_nombre: str,
    contacto_apellido: str,
    linkedin_url: str = "",
    ghl_url: str = "",
) -> Proyecto:
    with Session(engine) as session:
        # 1. Crear la empresa
        empresa = Empresa(nombre=empresa_nombre, web=empresa_web)
        session.add(empresa)
        session.commit()
        session.refresh(empresa)

        # 2. Crear el contacto
        contacto = Contacto(
            nombre=contacto_nombre,
            apellido=contacto_apellido,
            linkedin_url=linkedin_url,
            ghl_url=ghl_url,
        )
        session.add(contacto)
        session.commit()
        session.refresh(contacto)

        # 3. Crear el proyecto vinculado
        proyecto = Proyecto(
            empresa_id=empresa.id,
            contacto_id=contacto.id,
        )
        session.add(proyecto)
        session.commit()
        session.refresh(proyecto)

        return proyecto


def obtener_proyecto_db(proyecto_id: int) -> Proyecto | None:
    with Session(engine) as session:
        return session.get(Proyecto, proyecto_id)


def obtener_proyecto_completo(proyecto_id: int) -> dict | None:
    with Session(engine) as session:
        proyecto = session.get(Proyecto, proyecto_id)
        if not proyecto:
            return None
        empresa = session.get(Empresa, proyecto.empresa_id)
        contacto = session.get(Contacto, proyecto.contacto_id)
        asignaciones = session.exec(
            select(Asignacion).where(Asignacion.proyecto_id == proyecto_id)
        ).all()
        equipo = {}
        for asig in asignaciones:
            puesto = session.get(Puesto, asig.puesto_id)
            miembro = session.get(Miembro, asig.miembro_id)
            equipo[puesto.nombre] = miembro.email
        return {
            "id": proyecto.id,
            "empresa": empresa,
            "contacto": contacto,
            "estado": proyecto.estado,
            "started_date": proyecto.started_date,
            "end_date": proyecto.end_date,
            "tareas": session.exec(
                select(Tarea).where(Tarea.proyecto_id == proyecto_id)
            ).all(),
            "equipo": equipo,
            "notas": session.exec(
                select(Nota).where(Nota.proyecto_id == proyecto_id)
            ).all(),
        }


def activar_proyecto_db(
    proyecto_id: int,
    fecha_inicio: str,
    duracion_semanas: int = 14,
) -> dict | None:
    with Session(engine) as session:
        proyecto = session.get(Proyecto, proyecto_id)
        if not proyecto:
            return None

        proyecto.estado = "activo"
        proyecto.started_date = fecha_inicio

        # Traer asignaciones del equipo
        asignaciones = session.exec(
            select(Asignacion).where(Asignacion.proyecto_id == proyecto_id)
        ).all()

        equipo = {}
        for asig in asignaciones:
            puesto = session.get(Puesto, asig.puesto_id)
            equipo[puesto.nombre] = asig.miembro_id

        # 1. Tareas base
        for tarea_tmpl in TEMPLATE_BASE:
            miembro_id = equipo.get(tarea_tmpl["rol"])
            fecha = calcular_fecha_vencimiento(fecha_inicio, tarea_tmpl["semana"])
            session.add(
                Tarea(
                    proyecto_id=proyecto_id,
                    asignado_id=miembro_id,
                    nombre=tarea_tmpl["nombre"],
                    semana=tarea_tmpl["semana"],
                    fecha_vencimiento=fecha,
                )
            )

        # 2. Tres campañas normales
        for i, semana_inicio in enumerate(CAMPANAS_INICIALES):
            numero = i + 1
            for tmpl in TEMPLATES_CAMPANA["campana_normal"]:
                semana = semana_inicio + tmpl["offset"]
                session.add(
                    Tarea(
                        proyecto_id=proyecto_id,
                        asignado_id=equipo.get(tmpl["rol"]),
                        nombre=f"{tmpl['nombre']} - Campaña {numero}",
                        semana=semana,
                        fecha_vencimiento=calcular_fecha_vencimiento(
                            fecha_inicio, semana
                        ),
                    )
                )

        # 3. Chequeos dinámicos
        num_chequeos = (duracion_semanas - 3) // 2 + 1
        for num_chequeo in range(1, num_chequeos):
            semana = (num_chequeo * 2) + 1
            if semana <= duracion_semanas:
                session.add(
                    Tarea(
                        proyecto_id=proyecto_id,
                        asignado_id=equipo.get("account_manager"),
                        nombre=f"Chequeo {num_chequeo} (WU, FU, ADS, CLASES)",
                        semana=semana,
                        fecha_vencimiento=calcular_fecha_vencimiento(
                            fecha_inicio, semana
                        ),
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
            session.add(
                Tarea(
                    proyecto_id=proyecto_id,
                    asignado_id=equipo.get("account_manager"),
                    nombre=tc["nombre"],
                    semana=tc["semana"],
                    fecha_vencimiento=calcular_fecha_vencimiento(
                        fecha_inicio, tc["semana"]
                    ),
                )
            )

        session.commit()

        # 5. Marcar Onboarding COO como completado
        onboarding = session.exec(
            select(Tarea).where(
                Tarea.proyecto_id == proyecto_id,
                Tarea.nombre == "Onboarding COO",
            )
        ).first()
        if onboarding:
            onboarding.estado = "completado"
            onboarding.fecha_realizado = fecha_inicio
            session.commit()

    return obtener_proyecto_completo(proyecto_id)
