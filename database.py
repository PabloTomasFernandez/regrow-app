from sqlmodel import SQLModel, create_engine

DATABASE_URL = "sqlite:///regrow.db"

engine = create_engine(DATABASE_URL, echo=False)

def crear_tablas():
    SQLModel.metadata.create_all(engine)

if __name__ == "__main__":
    import db_modelos  # noqa: F401
    crear_tablas()
    print("Tablas creadas exitosamente")