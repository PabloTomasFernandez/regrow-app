from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = "sqlite:///regrow.db"

engine = create_engine(DATABASE_URL, echo=False)


def create_db() -> None:
    """Crea todas las tablas en la base de datos."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """Devuelve una sesión de base de datos."""
    return Session(engine)