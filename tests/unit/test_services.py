from datetime import date

from regrow.domain.models import TaskStatus
from regrow.domain.services import (
    generate_base_tasks,
    generate_checkups,
    generate_closing_tasks,
    next_friday,
    task_date_for_week,
)


class TestNextFriday:
    def test_from_monday(self) -> None:
        # Lunes 6 de abril 2026 → viernes 10
        assert next_friday(date(2026, 4, 6)) == date(2026, 4, 10)

    def test_from_friday(self) -> None:
        # Si ya es viernes, devuelve ese mismo viernes
        assert next_friday(date(2026, 4, 10)) == date(2026, 4, 10)

    def test_from_saturday(self) -> None:
        # Sábado 11 → viernes 17 (el siguiente)
        assert next_friday(date(2026, 4, 11)) == date(2026, 4, 17)

    def test_from_wednesday(self) -> None:
        # Miércoles 8 → viernes 10
        assert next_friday(date(2026, 4, 8)) == date(2026, 4, 10)


class TestTaskDateForWeek:
    def test_week_1_from_monday(self) -> None:
        # Onboarding lunes 6 abril, semana 1 → viernes 10
        assert task_date_for_week(date(2026, 4, 6), 1) == date(2026, 4, 10)

    def test_week_2(self) -> None:
        # Semana 2 = una semana después del viernes de semana 1
        assert task_date_for_week(date(2026, 4, 6), 2) == date(2026, 4, 17)

    def test_week_4(self) -> None:
        # Semana 4 = tres semanas después del viernes de semana 1
        assert task_date_for_week(date(2026, 4, 6), 4) == date(2026, 5, 1)


class TestGenerateBaseTasks:
    def test_count(self) -> None:
        tasks = generate_base_tasks(project_id=1, onboarding_date=date(2026, 4, 6))
        assert len(tasks) == 37

    def test_all_auto_generated(self) -> None:
        tasks = generate_base_tasks(project_id=1, onboarding_date=date(2026, 4, 6))
        assert all(t.is_auto_generated for t in tasks)

    def test_onboarding_coo_is_done(self) -> None:
        tasks = generate_base_tasks(project_id=1, onboarding_date=date(2026, 4, 6))
        coo_task = [t for t in tasks if t.title == "Onboarding COO"][0]
        assert coo_task.status == TaskStatus.done

    def test_week_1_tasks_fall_on_friday(self) -> None:
        tasks = generate_base_tasks(project_id=1, onboarding_date=date(2026, 4, 6))
        week_1 = [t for t in tasks if t.due_date == date(2026, 4, 10)]
        assert len(week_1) == 6  # 6 tareas en semana 1

    def test_project_id_assigned(self) -> None:
        tasks = generate_base_tasks(project_id=42, onboarding_date=date(2026, 4, 6))
        assert all(t.project_id == 42 for t in tasks)


class TestGenerateCheckups:
    def test_14_weeks_gives_5_checkups(self) -> None:
        tasks = generate_checkups(
            project_id=1, onboarding_date=date(2026, 4, 6), duration_weeks=14
        )
        assert len(tasks) == 5  # (14-3)//2 + 1 = 6? no, verifiquemos

    def test_checkup_names(self) -> None:
        tasks = generate_checkups(
            project_id=1, onboarding_date=date(2026, 4, 6), duration_weeks=14
        )
        assert tasks[0].title == "Chequeo 1 (WU, FU, ADS, CLASES)"
        assert tasks[-1].title == f"Chequeo {len(tasks)} (WU, FU, ADS, CLASES)"

    def test_checkup_weeks(self) -> None:
        # Para 14 semanas, chequeos en semanas 3, 5, 7, 9, 11
        tasks = generate_checkups(
            project_id=1, onboarding_date=date(2026, 4, 6), duration_weeks=14
        )
        expected_dates = [
            task_date_for_week(date(2026, 4, 6), 3),
            task_date_for_week(date(2026, 4, 6), 5),
            task_date_for_week(date(2026, 4, 6), 7),
            task_date_for_week(date(2026, 4, 6), 9),
            task_date_for_week(date(2026, 4, 6), 11),
        ]
        actual_dates = [t.due_date for t in tasks]
        assert actual_dates == expected_dates


class TestGenerateClosingTasks:
    def test_count(self) -> None:
        tasks = generate_closing_tasks(
            project_id=1, onboarding_date=date(2026, 4, 6), duration_weeks=14
        )
        assert len(tasks) == 3

    def test_aviso_week(self) -> None:
        tasks = generate_closing_tasks(
            project_id=1, onboarding_date=date(2026, 4, 6), duration_weeks=14
        )
        aviso = [t for t in tasks if "Aviso" in t.title][0]
        # duration - 5 = semana 9
        assert aviso.due_date == task_date_for_week(date(2026, 4, 6), 9)

    def test_informes_on_last_week(self) -> None:
        tasks = generate_closing_tasks(
            project_id=1, onboarding_date=date(2026, 4, 6), duration_weeks=14
        )
        informes = [t for t in tasks if "Informe" in t.title]
        last_friday = task_date_for_week(date(2026, 4, 6), 14)
        assert all(t.due_date == last_friday for t in informes)
