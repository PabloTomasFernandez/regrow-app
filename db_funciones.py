from sqlmodel import Session, select
from database import engine
from db_modelos import Empresa, Contacto, Proyecto


def listar_proyectos() -> list[Proyecto]:
    with Session(engine) as session:
        proyectos = session.exec(select(Proyecto)).all()
        return proyectos


def crear_proyecto_db(
    empresa_nombre: str,
    empresa_web: str,
    contacto_nombre: str,
    contacto_apellido: str,
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