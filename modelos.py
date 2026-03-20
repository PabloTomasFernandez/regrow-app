from pydantic import BaseModel


class Empresa(BaseModel):
    nombre: str
    web: str


class Contacto(BaseModel):
    nombre: str
    apellido: str
    linkedin_url: str = ""
    ghl_url: str = ""


class Equipo(BaseModel):
    pusher_coach: str = ""
    account_manager: str = ""
    copy: str = ""
    sdr: str = ""
    automater: str = ""
    coo: str = ""

class Proyecto(BaseModel):
    id: int
    empresa: Empresa
    contacto: Contacto
    estado: str = "inactivo"
    started_date: str = ""
    end_date: str = ""
    equipo: Equipo
    tareas: list = []
    notas: list = []

class ProyectoCrear(BaseModel):
    empresa: Empresa
    contacto: Contacto

class ProyectoActivar(BaseModel):
    fecha_inicio: str
    duracion_semanas: int = 14

