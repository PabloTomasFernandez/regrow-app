from sqlmodel import Session

from database import engine
from db_modelos import Miembro, Puesto


def seed():
    with Session(engine) as session:
        # Crear puestos
        puestos = [
            Puesto(nombre="pusher_coach"),
            Puesto(nombre="account_manager"),
            Puesto(nombre="copy"),
            Puesto(nombre="sdr"),
            Puesto(nombre="automater"),
            Puesto(nombre="coo"),
        ]
        for puesto in puestos:
            session.add(puesto)
        session.commit()

        # Crear miembros
        # Necesitás saber el id del puesto para asignarlo
        # Después del commit, cada puesto tiene su id
        for puesto in puestos:
            session.refresh(puesto)

        # Ahora podés crear miembros
        miembros = [
            Miembro(
                nombre="Candelaria",
                apellido="López García",
                email="clg@regrow.academy",
                puesto_id=puestos[0].id,  # pusher_coach
            ),
            Miembro(
                nombre="Rodrigo",
                apellido="Grondona",
                email="rg@regrow.academy",
                puesto_id=puestos[1].id,  # account_manager
            ),
            Miembro(
                nombre="Mariano",
                apellido="Bertona",
                email="mb@regrow.agency",
                puesto_id=puestos[1].id,  # account_manager
            ),
            Miembro(
                nombre="Gimena",
                apellido="Robles",
                email="mgr@regrow.academy",
                puesto_id=puestos[1].id,  # account_manager
            ),
            Miembro(
                nombre="Dolores",
                apellido="Mazzini",
                email="dm@regrow.academy",
                puesto_id=puestos[2].id,  # copy
            ),
            Miembro(
                nombre="Agustina",
                apellido="Repetto",
                email="ar@regrow.agency",
                puesto_id=puestos[3].id,  # sdr
            ),
            Miembro(
                nombre="Manuela",
                apellido="Godio Cabiron",
                email="mg@regrow.agency",
                puesto_id=puestos[3].id,  # sdr
            ),
            Miembro(
                nombre="Marcelo",
                apellido="Liceda",
                email="ml@regrow.academy",
                puesto_id=puestos[3].id,  # sdr
            ),
            Miembro(
                nombre="Pablo Tomás",
                apellido="Fernández",
                email="tf@regrow.agency",
                puesto_id=puestos[4].id,  # automater
            ),
            Miembro(
                nombre="Francisco",
                apellido="Verdager",
                email="fv@regrow.academy",
                puesto_id=puestos[5].id,  # coo
            ),

        ]
        for miembro in miembros:
            session.add(miembro)
        session.commit()

        print(f"Creados {len(puestos)} puestos y {len(miembros)} miembros")


if __name__ == "__main__":
    seed()