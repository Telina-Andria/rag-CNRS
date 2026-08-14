import logging
from collections.abc import Generator
from contextlib import contextmanager

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from src.db.interface.base import BaseDatabase

logger = logging.getLogger(__name__)


class PostgreSQLSettings(BaseSettings):
    """PostgreSQL configuration settings."""

    user: str = Field(default="postgres", description="PostgreSQL user")
    password: str = Field(default="postgres", description="PostgreSQL password")
    host: str = Field(default="localhost", description="PostgreSQL host")
    port: int = Field(default=5432, description="PostgreSQL port")
    db: str = Field(default="postgres", description="PostgreSQL database name")

    database_url: str | None = Field(
        default=None,
        description="PostgreSQL database URL (construite depuis user/password/host/port/db)",
    )
    echo_sql: bool = Field(default=False, description="Enable SQL query logging")
    pool_size: int = Field(default=20, description="Database connection pool size")
    max_overflow: int = Field(default=0, description="Maximum pool overflow")

    model_config = SettingsConfigDict(env_prefix="POSTGRES_", env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def build_database_url(self) -> "PostgreSQLSettings":
        """Construit database_url à partir des champs séparés si non fournie explicitement."""
        if self.database_url is None:
            self.database_url = (
                f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"
            )
        return self


Base = declarative_base()


class PostgreSQLDatabase(BaseDatabase):
    """PostgreSQL database implementation."""

    def __init__(self, config: PostgreSQLSettings):
        self.config = config
        self.engine: Engine | None = None
        self.session_factory: sessionmaker | None = None

    def startup(self) -> None:
        """Initialize the database connection."""
        try:
            database_url = self.config.database_url
            assert database_url is not None  # construite par le model_validator

            logger.info(f"Attempting to connect to PostgreSQL at: {self.config.host}")

            self.engine = create_engine(
                database_url,
                echo=self.config.echo_sql,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_pre_ping=True,  # Verify connections before use
            )

            self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)

            # Test the connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                logger.info("Database connection test successful")

            # Create tables if they don't exist (idempotent operation)
            inspector = inspect(self.engine)
            existing_tables = inspector.get_table_names()

            Base.metadata.create_all(bind=self.engine)

            updated_tables = inspector.get_table_names()
            new_tables = set(updated_tables) - set(existing_tables)

            if new_tables:
                logger.info(f"Created new tables: {', '.join(new_tables)}")
            else:
                logger.info("All tables already exist - no new tables created")

            logger.info("PostgreSQL database initialized successfully")
            logger.info(f"Database: {self.engine.url.database}")
            logger.info(f"Total tables: {', '.join(updated_tables) if updated_tables else 'None'}")

        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL database: {e}")
            raise

    def teardown(self) -> None:
        """Close the database connection."""
        if self.engine:
            self.engine.dispose()
            logger.info("PostgreSQL database connections closed")

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session."""
        if not self.session_factory:
            raise RuntimeError("Database not initialized. Call startup() first.")

        session = self.session_factory()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
