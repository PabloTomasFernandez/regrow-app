from funciones import crear_tarea, calcular_fecha_vencimiento, crear_proyecto, contar_campanas


def test_crear_tarea():
    tarea = crear_tarea("Onboarding", "clg@regrow.academy", 1, "2026-03-27")
    assert tarea["nombre"] == "Onboarding"
    assert tarea["asignado_a"] == "clg@regrow.academy"
    assert tarea["estado"] == "sin_iniciar"
    assert tarea["semana"] == 1
    assert tarea["comentarios"] == []

def test_calcular_fecha_vencimiento():
    fecha = calcular_fecha_vencimiento("2025-11-14", 2)
    assert fecha == "2025-11-21"

def test_crear_proyecto():
    proyectos = []
    proyecto = crear_proyecto(proyectos, "TestCo", "www.test.com", "Juan", "Lopez")
    assert proyecto["id"] == 1
    assert proyecto["estado"] == "inactivo"
    assert proyecto["equipo"]["account_manager"] == ""
    assert len(proyectos) == 1

def test_contar_campanas():
    proyecto = {
        "tareas": [
            {"nombre": "Propuesta - Campaña 1"},
            {"nombre": "Informe - Campaña 1"},
            {"nombre": "Propuesta - Campaña 2"},
            {"nombre": "Propuesta - Evento 1"},
        ]
    }
    assert contar_campanas(proyecto, "campana_normal") == 2
    assert contar_campanas(proyecto, "evento") == 1