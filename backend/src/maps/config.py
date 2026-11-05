import os

DATABASE_URL: str = os.environ.get(
    "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@postgres:5432/postgres"
)
