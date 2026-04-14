# CLAUDE.md — Regrow App

## Qué es este proyecto

App interna de gestión de proyectos para Regrow Agency, una agencia de
prospección B2B que implementa el método PACS (Prospección, Autoridad,
Conversación, Seguimiento) para sus clientes vía LinkedIn.

Reemplaza spreadsheets y Slack Lists con una herramienta centralizada.

## Stack

- Python 3.13 (pinned en .python-version)
- uv para dependencias
- FastAPI (fastapi dev / fastapi run)
- SQLModel + SQLite
- ruff (reglas E/F/I/UP, line length 88)
- pyright strict mode
- pytest

## Arquitectura hexagonal

```
src/regrow/
├── domain/                    # Lógica pura. SIN imports de FastAPI ni SQLModel.
│   ├── models.py              # Entidades: Company, Client, TeamMember, Project, Task
│   │                          # Enums: ProjectStatus, TaskStatus, TeamRole
│   ├── services.py            # next_friday, task_date_for_week, generate_base_tasks,
│   │                          # generate_checkups, generate_closing_tasks,
│   │                          # generate_campaign_tasks (no wired yet)
│   └── templates.py           # Templates de tareas + equipo
├── adapters/
│   ├── api/                   # FastAPI routers
│   │   ├── clients.py         # /clients — CRUD
│   │   ├── companies.py       # /companies — CRUD
│   │   ├── projects.py        # /projects — create + activate
│   │   └── schemas.py         # Pydantic request/response
│   └── db/                    # SQLModel + SQLite
│       ├── engine.py          # Engine + get_session
│       ├── models.py          # CompanyDB, ClientDB, TeamMemberDB, ProjectDB, TaskDB
│       └── repository.py      # Funciones de acceso a BD
├── main.py                    # Entry point FastAPI
tests/
├── unit/
│   └── test_services.py       # 18 tests (next_friday, tasks, checkups, closing)
└── integration/               # Vacío — pendiente
```

**Regla estricta**: domain/ NO importa nada de FastAPI ni SQLModel.

## Convenciones de código

- Nombres en inglés en todo el código (Company no Empresa, Task no Tarea)
- __tablename__ requiere `# type: ignore[assignment]` para pyright strict
- Foreign keys siempre del lado del "muchos"
- Type hints en todos los parámetros y retornos
- StrEnum para estados (ProjectStatus, TaskStatus, TeamRole)
- Domain models son Pydantic BaseModel, DB models son SQLModel con table=True

## Tablas existentes (5)

| Tabla DB | Tablename | Campos clave |
|----------|-----------|-------------|
| CompanyDB | companies | name, industry, linkedin_company, website |
| ClientDB | clients | name, apellido, email, company_id(FK), linkedin_profile |
| TeamMemberDB | team_members | name, role(TeamRole), email, is_admin |
| ProjectDB | projects | name, client_id(FK), status, activated_at, duration_weeks=14 |
| TaskDB | tasks | project_id(FK), assigned_to(FK), title, status, due_date, week |

## Tablas a crear — Campañas y secuencias

### Tablas faltantes del core (4)

Estas tablas se diseñaron pero no se implementaron aún:

| Tabla | Campos clave | Nota |
|-------|-------------|------|
| AssignmentDB | project_id(FK), member_id(FK), role(TeamRole) | Quién tiene qué rol en cada proyecto |
| CommentDB | task_id(FK), author_id(FK), text, created_at | Comentarios en tareas |
| NoteDB | project_id(FK), author_id(FK), text, created_at | Notas generales del proyecto |

### Tablas de campañas (5)

| Tabla | Campos clave | Nota |
|-------|-------------|------|
| CampaignDetailDB | project_id(FK), number, type(normal/event), industry, country, company_size, event_name, copy_status | Una campaña de outreach |
| BuyerPersonaDB | campaign_detail_id(FK), position, trigger, attendee_type, lemlist_campaign_id, status | Cada BP = 1 campaña Lemlist |
| SequenceDB | buyer_persona_id(FK), type(linkedin/email_connected/email_cold) | Secuencia de mensajes |
| MessageDB | sequence_id(FK), order, subject, body, delay_days, approved | Un mensaje individual |
| ValidationDB | message_id(FK), author_id(FK), text, approved, created_at | Feedback del cliente |

## Flujo de negocio

### Activación de proyecto
Al activar: genera 37 base tasks + checkups((n-3)//2) + 3 closing tasks.
Onboarding COO se auto-completa. generate_campaign_tasks existe pero no
está conectado a los routers aún.

### Flujo de campañas (semanas 3, 7, 11)
```
1. AM → Prospecting Canvas (industry, country, size, buyer personas)
2. SDR → Prospect leads según canvas
3. Copy → Message sequences por buyer persona
4. Client → Validates (back-and-forth con comments)
5. Automater → Creates Lemlist campaigns
   Cada buyer persona = 1 campaña en Lemlist
   → saves lemlist_campaign_id en BuyerPersonaDB
```

### Validación del copy
- Copy creates messages → status "draft"
- Sends to review → "in_review"
- Client comments per message (back and forth)
- All messages of a BP approved → BP "validated"
- ALL BPs of campaign validated → campaign "copy_validated"
- Automater sees: "ready for Lemlist"

## Reglas de negocio

- lemlist_campaign_id va en BuyerPersonaDB, NO en CampaignDetailDB
- Industry, country, size, position, trigger: catálogo autocreciente
- Proyectos default 14 semanas
- Campañas en semanas 3, 7, 11 (no al activar)
- Checkups: (n-3)//2

## Qué NO hacer

- NO importar FastAPI ni SQLModel en domain/
- NO poner lógica de negocio en los routers
- NO crear endpoints sin tests
- NO hardcodear strings de estado (usar StrEnum)

## Comandos

```bash
uv run fastapi dev src/regrow/main.py    # Dev server
uv run pytest                             # Tests
uv run ruff check .                       # Lint
uv run ruff format .                      # Format
uv run pyright                            # Type check
```

## Roadmap inmediato

1. ✅ Arquitectura hexagonal (HECHO)
2. ✅ Activación de proyecto con tareas auto (HECHO)
3. → Agregar tablas de campañas (domain + db + routers)
4. Dashboard Streamlit con estado de todos los clientes
5. Integración Slack vía n8n
6. Agentes IA (clasificador, scoring, SDR writer)