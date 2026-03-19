# Regrow App

Gestor interno de proyectos para Regrow. Controla clientes, equipos,
tareas y estado de cada proyecto desde una interfaz web.

## Qué hace

- Panel con métricas: proyectos activos, pausados, tareas pendientes
- Tabla de proyectos filtrable por estado (activo/inactivo/pausado)
- Vista de tareas por miembro del equipo
- Formulario para crear proyectos nuevos
- Notas por proyecto (ej: "cliente no pagó, pausar tareas")
- Datos persistidos en JSON local

## Stack

- Python 3.12+
- Streamlit
- Ruff (linter/formatter)
- uv (gestor de dependencias)

## Cómo correrlo
```bash
git clone git clone https://github.com/PabloTomasFernandez/regrow-app.git
cd regrow-app
uv sync
uv run streamlit run app.py
```

Se abre en `http://localhost:8501`.

## Qué viene

- [ ] Templates de tareas automáticos por proyecto
- [ ] Asignación de equipo desde la interfaz
- [ ] Integración con API de Lemlist (métricas de campañas)
- [ ] Autenticación por rol (admin, equipo, cliente)
- [ ] Deploy a producción