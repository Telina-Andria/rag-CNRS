import pytest
from sqlalchemy import text
from testcontainers.community.postgres import PostgresContainer

from src.db.interface.postgresql import PostgreSQLDatabase, PostgreSQLSettings


@pytest.fixture
def pd_container():
    with PostgresContainer("postgres:16-alpine") as pg:
        yield pg


def test_startup_and_session(pd_container):
    config = PostgreSQLSettings(database_url=pd_container.get_connection_url())
    db = PostgreSQLDatabase(config=config)

    db.startup()
    with db.get_session() as session:
        result = session.execute(text("SELECT 1")).scalar()
        assert result == 1

    db.teardown()


def test_get_session_before_startup_raises():
    db = PostgreSQLDatabase(config=PostgreSQLSettings())
    with pytest.raises(RuntimeError):
        with db.get_session():
            pass
