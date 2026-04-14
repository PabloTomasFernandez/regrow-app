from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from regrow.adapters.api import campaigns, clients, companies, projects
from regrow.adapters.db.repository import Repository
from regrow.main import app


@pytest.fixture
def engine() -> Iterator[Engine]:
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(test_engine)
    yield test_engine
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture
def session(engine: Engine) -> Iterator[Session]:
    with Session(engine) as s:
        yield s


@pytest.fixture
def client(session: Session) -> Iterator[TestClient]:
    def override_get_repo() -> Repository:
        return Repository(session)

    app.dependency_overrides[companies.get_repo] = override_get_repo
    app.dependency_overrides[clients.get_repo] = override_get_repo
    app.dependency_overrides[projects.get_repo] = override_get_repo
    app.dependency_overrides[campaigns.get_repo] = override_get_repo

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
