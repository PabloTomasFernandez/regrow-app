from datetime import date

from regrow.domain.services import next_friday, task_date_for_week


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