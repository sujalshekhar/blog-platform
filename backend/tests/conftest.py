import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db

# Create an in-memory SQLite database engine for testing.
# StaticPool is used to prevent the in-memory database from being closed when connections are closed.
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db() -> Generator[None, None, None]:
    # Create the database schema before running tests
    Base.metadata.create_all(bind=engine)
    yield
    # Drop schema after tests are done
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    # Override get_db dependency to use the test database session
    def _override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

# ── Shared Test Helpers ─────────────────────────────────────────────────────────

from app.models.user import User
from app.models.blog import Blog
from app.enums.role import UserRole
from app.enums.blog_status import BlogStatus
from app.core.security import create_access_token
from datetime import timedelta

def make_user(db: Session, email: str, first_name: str = "Test", role: UserRole = UserRole.USER) -> User:
    user = User(
        first_name=first_name,
        last_name="User",
        email=email,
        password_hash="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW", # "password"
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def make_blog(db: Session, user: User, group_id: int = 1, status: BlogStatus = BlogStatus.DRAFT) -> Blog:
    blog = Blog(
        blog_group_id=group_id,
        version=1,
        title="Test Blog",
        content="Some content",
        status=status,
        author_id=user.id,
    )
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return blog

def get_auth_headers_for_user(user: User) -> dict:
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
def auth_headers(db_session: Session) -> dict:
    user = make_user(db_session, "user@example.com", "TestUser", UserRole.USER)
    return get_auth_headers_for_user(user)

@pytest.fixture
def approver_headers(db_session: Session) -> dict:
    user = make_user(db_session, "approver@example.com", "Approver", UserRole.APPROVER)
    return get_auth_headers_for_user(user)

@pytest.fixture
def admin_headers(db_session: Session) -> dict:
    user = make_user(db_session, "admin@example.com", "Admin", UserRole.ADMIN)
    return get_auth_headers_for_user(user)
