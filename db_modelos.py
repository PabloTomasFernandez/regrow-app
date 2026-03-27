from sqlmodel import Field, SQLModel


class Empresa(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    web: str
    linkedin_company: str = ""


class Contacto(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    apellido: str
    linkedin_url: str = ""
    ghl_url: str = ""


class Puesto(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str


class Miembro(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    apellido: str
    email: str
    puesto_id: int = Field(foreign_key="puesto.id")


class Proyecto(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    empresa_id: int = Field(foreign_key="empresa.id")
    contacto_id: int = Field(foreign_key="contacto.id")
    estado: str = "inactivo"
    started_date: str = ""
    end_date: str = ""


class Asignacion(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    proyecto_id: int = Field(foreign_key="proyecto.id")
    miembro_id: int = Field(foreign_key="miembro.id")
    puesto_id: int = Field(foreign_key="puesto.id")


class Tarea(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    proyecto_id: int = Field(foreign_key="proyecto.id")
    asignado_id: int | None = Field(default=None, foreign_key="miembro.id")
    nombre: str
    estado: str = "sin_iniciar"
    semana: int = 0
    fecha_vencimiento: str = ""
    fecha_realizado: str = ""


class Comentario(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tarea_id: int = Field(foreign_key="tarea.id")
    autor_id: int = Field(foreign_key="miembro.id")
    texto: str
    fecha: str


class Nota(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    proyecto_id: int = Field(foreign_key="proyecto.id")
    autor_id: int = Field(foreign_key="miembro.id")
    texto: str
    fecha: str