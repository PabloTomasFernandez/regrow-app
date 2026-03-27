from fastapi import FastAPI, HTTPException

from db_funciones import (
    crear_proyecto_db,
    listar_proyectos,
    obtener_proyecto_completo,
)
from modelos import ProyectoCrear

app = FastAPI(title="Regrow API")


@app.get("/")
def inicio():
    return {"mensaje": "Regrow API funcionando"}


@app.get("/proyectos")
def get_proyectos():
    return listar_proyectos()


@app.get("/proyectos/{proyecto_id}")
def get_proyecto(proyecto_id: int):
    proyecto = obtener_proyecto_completo(proyecto_id)
    if not proyecto:
        raise HTTPException(
            status_code=404, detail="Proyecto no encontrado"
        )
    return proyecto


@app.post("/proyectos")
def nuevo_proyecto(datos: ProyectoCrear):
    proyecto = crear_proyecto_db(
        empresa_nombre=datos.empresa.nombre,
        empresa_web=datos.empresa.web,
        contacto_nombre=datos.contacto.nombre,
        contacto_apellido=datos.contacto.apellido,
        linkedin_url=datos.contacto.linkedin_url,
        ghl_url=datos.contacto.ghl_url,
    )
    return obtener_proyecto_completo(proyecto.id)


# @app.post("/proyectos/{proyecto_id}/activar")
# def activar(proyecto_id: int, datos: ProyectoActivar):
#     proyectos = cargar_proyectos()
#     for proyecto in proyectos:
#         if proyecto["id"] == proyecto_id:
#             roles_vacios = [
#                 rol for rol, email in proyecto["equipo"].items() if not email
#             ]
#             if roles_vacios:
#                 raise HTTPException(
#                     status_code=400,
#                     detail=f"Faltan roles: {', '.join(roles_vacios)}",
#                 )
#             activar_proyecto(
#                 proyecto, proyectos, datos.fecha_inicio, datos.duracion_semanas
#             )
#             return proyecto
#     raise HTTPException(status_code=404, detail="Proyecto no encontrado")
