# backend/tests/conftest.py
import os

# Must be set BEFORE any backend imports to prevent scheduler startup
os.environ["DISABLE_SCHEDULER"] = "true"

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as OrmSession


@pytest.fixture
def db_engine():
    # Import Base here (after env var is set) to avoid transitive backend.main import
    from backend.db.models import Base

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    connection = engine.connect()
    Base.metadata.create_all(bind=connection)
    yield engine, connection
    connection.close()
    engine.dispose()


@pytest.fixture
def client(db_engine):
    from fastapi.testclient import TestClient  # deferred import
    from backend.db.database import get_db
    from backend.main import app

    _, connection = db_engine

    def override_get_db():
        db = OrmSession(bind=connection)
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
