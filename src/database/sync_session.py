from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.session_postgresql import POSTGRESQL_DATABASE_URL

sync_database_url = POSTGRESQL_DATABASE_URL.replace(
    "postgresql+asyncpg", "postgresql+psycopg2"
)
sync_postgresql_engine = create_engine(sync_database_url, echo=False)
SyncSessionLocal = sessionmaker(
    bind=sync_postgresql_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)
