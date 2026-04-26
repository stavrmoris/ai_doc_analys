from collections.abc import Iterator

import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base, create_db_engine, create_session_factory
import app.db.models  # noqa: F401


@pytest.fixture
def db_engine(tmp_path) -> Iterator[Engine]:
    database_path = tmp_path / "test.db"
    engine = create_db_engine(f"sqlite:///{database_path}")
    Base.metadata.create_all(engine)

    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def db_session(db_engine) -> Iterator[Session]:
    SessionFactory = create_session_factory(db_engine)

    session = SessionFactory()
    try:
        yield session
    finally:
        session.close()
