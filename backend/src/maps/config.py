import os

DATABASE_URL: str = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/postgres"
)
