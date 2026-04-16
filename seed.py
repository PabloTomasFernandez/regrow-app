from datetime import date

from sqlmodel import Session, SQLModel

from regrow.adapters.db.engine import engine
from regrow.adapters.db.models import (
    BuyerPersonaDB,
    CampaignDetailDB,
    ClientDB,
    CompanyDB,
    ProjectDB,
    TaskDB,
    TaskTemplateDB,
    TeamMemberDB,
)
from regrow.domain.models import ProjectStatus, TeamRole
from regrow.domain.services import (
    generate_base_tasks,
    generate_checkups,
    generate_closing_tasks,
)
from regrow.domain.templates import BASE_TASKS


def reset_db() -> None:
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


def seed_team(session: Session) -> None:
    members = [
        TeamMemberDB(name="Rodrigo Grondona", role=TeamRole.account_manager),
        TeamMemberDB(name="Loli Mazzini", role=TeamRole.copy),
        TeamMemberDB(name="Marcelo Liceda", role=TeamRole.copy),
        TeamMemberDB(name="Josemaría Robles", role=TeamRole.pusher),
        TeamMemberDB(name="Tomás Fernandez", role=TeamRole.automater),
        TeamMemberDB(name="Francisco Verdaguer", role=TeamRole.coo, is_admin=True),
    ]
    session.add_all(members)
    session.commit()


def seed_project(
    session: Session,
    company_name: str,
    client_first: str,
    client_last: str,
    project_name: str,
    activated_at: date | None,
) -> ProjectDB:
    company = CompanyDB(name=company_name)
    session.add(company)
    session.commit()
    session.refresh(company)
    assert company.id is not None

    client = ClientDB(name=client_first, apellido=client_last, company_id=company.id)
    session.add(client)
    session.commit()
    session.refresh(client)
    assert client.id is not None

    project = ProjectDB(
        name=project_name,
        client_id=client.id,
        status=ProjectStatus.active if activated_at else ProjectStatus.draft,
        activated_at=activated_at,
    )
    session.add(project)
    session.commit()
    session.refresh(project)
    assert project.id is not None

    if activated_at is not None:
        tasks = generate_base_tasks(project.id, activated_at)
        tasks.extend(
            generate_checkups(project.id, activated_at, project.duration_weeks)
        )
        tasks.extend(
            generate_closing_tasks(project.id, activated_at, project.duration_weeks)
        )
        for t in tasks:
            session.add(
                TaskDB(
                    project_id=t.project_id,
                    title=t.title,
                    description=t.description,
                    notes=t.notes,
                    status=t.status,
                    assigned_to=t.assigned_to,
                    due_date=t.due_date,
                    is_auto_generated=t.is_auto_generated,
                )
            )
        session.commit()

    return project


def seed_campaign(
    session: Session,
    project_id: int,
    number: int,
    industry: str,
    country: str,
    company_size: str,
    copy_status: str,
    buyer_personas: list[tuple[str, str]],
    bp_status: str = "draft",
) -> None:
    campaign = CampaignDetailDB(
        project_id=project_id,
        number=number,
        campaign_type="normal",
        industry=industry,
        country=country,
        company_size=company_size,
        copy_status=copy_status,
    )
    session.add(campaign)
    session.commit()
    session.refresh(campaign)
    assert campaign.id is not None

    for position, trigger in buyer_personas:
        session.add(
            BuyerPersonaDB(
                campaign_detail_id=campaign.id,
                position=position,
                trigger=trigger,
                status=bp_status,
            )
        )
    session.commit()


def seed_task_templates(session: Session) -> None:
    for t in BASE_TASKS:
        session.add(
            TaskTemplateDB(title=t.name, role=t.role, week=t.week, category="base")
        )
    session.commit()


def main() -> None:
    reset_db()

    with Session(engine) as session:
        seed_team(session)
        seed_task_templates(session)

        prod4dev = seed_project(
            session,
            "Prod4dev",
            "Matías",
            "Gómez",
            "Prod4dev PACS",
            date(2026, 1, 23),
        )
        seed_project(
            session,
            "Paydece",
            "Felipe",
            "Ruiz",
            "Paydece PACS",
            date(2025, 12, 19),
        )
        mbf = seed_project(
            session,
            "Make Business Flow",
            "Karina",
            "Lopez",
            "MBF PACS",
            date(2026, 1, 23),
        )
        pixeldreams = seed_project(
            session,
            "Pixeldreams",
            "Alex",
            "Martín",
            "Pixeldreams PACS",
            date(2026, 1, 24),
        )
        seed_project(
            session,
            "Winclap",
            "Lorenzo",
            "Silva",
            "Winclap PACS",
            date(2026, 4, 7),
        )

        assert prod4dev.id is not None
        assert mbf.id is not None
        assert pixeldreams.id is not None

        seed_campaign(
            session,
            prod4dev.id,
            number=1,
            industry="SaaS",
            country="AR",
            company_size="50-200",
            copy_status="validated",
            buyer_personas=[
                ("CTO", "hiring developers"),
                ("Head of Engineering", "scaling team"),
            ],
            bp_status="validated",
        )
        seed_campaign(
            session,
            prod4dev.id,
            number=2,
            industry="Fintech",
            country="AR",
            company_size="10-50",
            copy_status="in_review",
            buyer_personas=[
                ("CEO", "series A"),
                ("VP Engineering", "tech debt"),
                ("Product Lead", "new launch"),
            ],
            bp_status="in_review",
        )

        seed_campaign(
            session,
            mbf.id,
            number=1,
            industry="Consulting",
            country="AR",
            company_size="10-50",
            copy_status="validated",
            buyer_personas=[
                ("Operations Manager", "process automation"),
                ("COO", "scaling ops"),
            ],
            bp_status="validated",
        )
        seed_campaign(
            session,
            mbf.id,
            number=2,
            industry="Manufacturing",
            country="AR",
            company_size="200+",
            copy_status="in_review",
            buyer_personas=[
                ("Plant Manager", "digital transformation"),
                ("CIO", "ERP migration"),
            ],
            bp_status="in_review",
        )

        seed_campaign(
            session,
            pixeldreams.id,
            number=1,
            industry="E-commerce",
            country="AR",
            company_size="10-50",
            copy_status="draft",
            buyer_personas=[
                ("Marketing Director", "rebranding"),
                ("Head of Design", "new product line"),
                ("Founder", "seeking growth"),
            ],
            bp_status="draft",
        )

    print("Seed completed.")


if __name__ == "__main__":
    main()
