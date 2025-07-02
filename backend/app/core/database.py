"""
Database Configuration for GestorLead Studio
Task: 1.8 - Integrate ORM Models with FastAPI
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    poolclass=QueuePool,
    echo=settings.DEBUG,
    future=True,
    # Connection arguments
    connect_args={
        "options": "-c timezone=utc"
    }
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine,
    expire_on_commit=False
)


# Event listeners for better logging and debugging
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set database-specific settings on connection"""
    if settings.DEBUG:
        logger.info("New database connection established")


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """Log connection checkout"""
    if settings.DEBUG:
        logger.debug("Connection checked out from pool")


@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    """Log connection checkin"""
    if settings.DEBUG:
        logger.debug("Connection checked in to pool")


def get_db_session():
    """
    Get database session for manual use outside FastAPI dependency injection
    """
    return SessionLocal()


def test_connection():
    """
    Test database connection
    """
    try:
        with engine.connect() as connection:
            result = connection.execute("SELECT 1")
            logger.info("Database connection test successful")
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False
