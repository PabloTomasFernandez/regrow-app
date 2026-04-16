from datetime import date, timedelta

from regrow.domain.models import Task, TaskStatus
from regrow.domain.templates import (
    BASE_TASKS,
    CampaignTaskTemplate,
    TaskTemplate,
)


def next_friday(from_date: date) -> date:
    """Calcula el viernes más cercano desde una fecha dada."""
    days_ahead = 4 - from_date.weekday()  # 4 = viernes
    if days_ahead < 0:
        days_ahead += 7
    return from_date + timedelta(days=days_ahead)


def task_date_for_week(onboarding_date: date, week: int) -> date:
    """Calcula la fecha de una tarea según su semana relativa al onboarding.

    Semana 1 = el viernes de la semana del onboarding.
    Semana 2 = el viernes siguiente, etc.
    """
    base_friday = next_friday(onboarding_date)
    return base_friday + timedelta(weeks=week - 1)


def generate_base_tasks(
    project_id: int,
    onboarding_date: date,
    templates: list[TaskTemplate] | None = None,
) -> list[Task]:
    """Genera las tareas base del proyecto al activar."""
    source = templates if templates is not None else BASE_TASKS
    tasks: list[Task] = []

    for template in source:
        task = _task_from_template(
            project_id=project_id,
            template=template,
            due_date=task_date_for_week(onboarding_date, template.week),
        )
        if template.name == "Onboarding COO":
            task.status = TaskStatus.done

        tasks.append(task)

    return tasks


def generate_campaign_tasks(
    project_id: int,
    campaign_start_week: int,
    onboarding_date: date,
    campaign_templates: list[CampaignTaskTemplate],
    campaign_label: str,
) -> list[Task]:
    """Genera las tareas de una campaña específica."""
    tasks: list[Task] = []

    for template in campaign_templates:
        actual_week = campaign_start_week + template.week_offset
        due_date = task_date_for_week(onboarding_date, actual_week)

        task = Task(
            project_id=project_id,
            title=f"{template.name} - {campaign_label}",
            status=TaskStatus.pending,
            due_date=due_date,
            is_auto_generated=True,
        )
        tasks.append(task)

    return tasks


def generate_checkups(
    project_id: int,
    onboarding_date: date,
    duration_weeks: int,
) -> list[Task]:
    """Genera los chequeos periódicos según la duración del proyecto."""
    num_checkups = (duration_weeks - 3) // 2
    tasks: list[Task] = []

    for n in range(1, num_checkups + 1):
        week = (n * 2) + 1
        tasks.append(
            Task(
                project_id=project_id,
                title=f"Chequeo {n} (WU, FU, ADS, CLASES)",
                status=TaskStatus.pending,
                due_date=task_date_for_week(onboarding_date, week),
                is_auto_generated=True,
            ),
        )

    return tasks


def generate_closing_tasks(
    project_id: int,
    onboarding_date: date,
    duration_weeks: int,
) -> list[Task]:
    """Genera las tareas de cierre del proyecto."""
    return [
        Task(
            project_id=project_id,
            title="Aviso 1 mes para que finalice el proyecto",
            status=TaskStatus.pending,
            due_date=task_date_for_week(onboarding_date, duration_weeks - 5),
            is_auto_generated=True,
        ),
        Task(
            project_id=project_id,
            title="Informe cierre interno",
            status=TaskStatus.pending,
            due_date=task_date_for_week(onboarding_date, duration_weeks),
            is_auto_generated=True,
        ),
        Task(
            project_id=project_id,
            title="Informe cierre cliente",
            status=TaskStatus.pending,
            due_date=task_date_for_week(onboarding_date, duration_weeks),
            is_auto_generated=True,
        ),
    ]


def _task_from_template(
    project_id: int,
    template: TaskTemplate,
    due_date: date,
) -> Task:
    """Crea una Task desde un TaskTemplate."""
    return Task(
        project_id=project_id,
        title=template.name,
        status=TaskStatus.pending,
        due_date=due_date,
        is_auto_generated=True,
    )
