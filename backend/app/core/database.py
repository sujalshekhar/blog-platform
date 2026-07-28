from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from app.core.config import settings

# For PostgreSQL, we configure connection pooling.
# pool_size: The number of connections to keep open inside the pool.
# max_overflow: The number of connections to allow in addition to pool_size.
# pool_recycle: Recycle connections after this number of seconds (prevent connection timeout).
# pool_pre_ping: Check connection health before using it.
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_recycle=3600,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# SQLAlchemy 2.x Declarative Base style
class Base(DeclarativeBase):
    pass

# Dependency to get db session in FastAPI routes
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
