from fastapi import FastAPI, HTTPException

from funciones import cargar_proyectos, crear_proyecto, activar_proyecto, guardar_proyectos
from modelos import Proyecto, ProyectoActivar, ProyectoCrear

app = FastAPI(title="Regrow API")


@app.get("/")
def inicio():
    return {"mensaje": "Regrow API funcionando"}

@app.get("/proyectos", response_model=list[Proyecto])
def listar_proyectos():
    return cargar_proyectos()

@app.post("/proyectos/{proyecto_id }", response_model=Proyecto)
def obtener_proyecto(proyecto_id: int):
    proyectos = cargar_proyectos()
    for proyecto in proyectos:
        if proyecto["id"] == proyecto_id:
            return proyecto
    raise HTTPException(status_code=404, detail="Proyecto no encontrado")

@app.post("/proyectos", response_model=Proyecto)
def nuevo_proyecto(datos: ProyectoCrear):
    proyectos = cargar_proyectos()
    proyecto = crear_proyecto(
        proyectos=proyectos,
        empresa_nombre=datos.empresa.nombre,
        empresa_web=datos.empresa.web,
        contacto_nombre=datos.contacto.nombre,
        contacto_apellido=datos.contacto.apellido,
        linkedin_url=datos.contacto.linkedin_url,
        ghl_url=datos.contacto.ghl_url,
    )
    return proyecto

@app.post("/proyectos/{proyecto_id}/activar")
def activar(proyecto_id: int, datos: ProyectoActivar):
    proyectos = cargar_proyectos()
    for proyecto in proyectos:
        if proyecto["id"] == proyecto_id:
            roles_vacios = [rol for rol, email in proyecto["equipo"].items() if not email]
            if roles_vacios:
                raise HTTPException(
                    status_code=400,
                    detail=f"Faltan roles: {', '.join(roles_vacios)}",
                )
            activar_proyecto(proyecto, proyectos, datos.fecha_inicio, datos.duracion_semanas)
            return proyecto
    raise HTTPException(status_code=404, detail="Proyecto no encontrado")
