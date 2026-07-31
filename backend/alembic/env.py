import sys
import os
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool
from alembic import context

# ── Path setup ─────────────────────────────────────────────────────────────────
# Ensure the backend root is on sys.path so app.* imports resolve correctly
# when Alembic is run from the backend/ directory.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# ── App imports ────────────────────────────────────────────────────────────────
# Import settings first so the DATABASE_URL is available.
from app.core.config import settings  # noqa: E402

# Import Base so target_metadata is populated.
from app.core.database import Base  # noqa: E402

# Import every model module so SQLAlchemy registers them with Base.metadata
# before Alembic inspects it.  Add new models here as they are created.
import app.models.user          # noqa: F401
import app.models.blog          # noqa: F401
import app.models.chat          # noqa: F401
import app.models.message       # noqa: F401
import app.models.notification  # noqa: F401
import app.models.feature_request  # noqa: F401

# ── Alembic config ─────────────────────────────────────────────────────────────
config = context.config

# Override sqlalchemy.url with the value from our .env file so credentials are
# never stored in alembic.ini.
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Set up Python logging from alembic.ini.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# This is the metadata object that Alembic will diff against the live DB.
target_metadata = Base.metadata


# ── Migration runners ──────────────────────────────────────────────────────────

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine.
    Useful for generating SQL scripts without a live DB connection.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Detect column-type changes (e.g. Enum value additions).
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    Creates an Engine and associates a connection with the migration context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Detect column-type changes (e.g. Enum value additions).
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

