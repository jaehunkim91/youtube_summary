# backend/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from backend.db.models import Base
from backend.db.database import get_db

@pytest.fixture
def db_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    # Use a single connection so all sessions share the same in-memory DB
    connection = engine.connect()
    Base.metadata.create_all(bind=connection)
    yield engine, connection
    connection.close()
    engine.dispose()

@pytest.fixture
def client(db_engine):
    engine, connection = db_engine
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    from backend.main import app
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
