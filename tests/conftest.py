import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base


@pytest.fixture
def db_session():
    # Use a shared-cache in-memory database so that all connections
    # (including those from the async middleware running in a
    # different thread via anyio.from_thread) see the same data.
    engine = create_engine(
        "sqlite:///file:testdb?mode=memory&cache=shared&uri=true",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def client(db_session):
    import main
    from main import app, get_db

    # Override SessionLocal so the middleware uses the test session
    # instead of creating a session to the real database.
    original_session_local = main.SessionLocal
    main.SessionLocal = lambda: db_session

    # Prevent the middleware's "finally: db.close()" from closing
    # the test session, since the test needs to continue querying it.
    _original_close = db_session.close
    db_session.close = lambda: None

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    db_session.close = _original_close
    main.SessionLocal = original_session_local
    app.dependency_overrides.clear()
