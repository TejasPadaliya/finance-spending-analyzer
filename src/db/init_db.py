"""Create database tables idempotently.

Run with: python -m src.db.init_db
"""

from src.db import engine
from src.db.models import Base


def init_db() -> None:
    """Create all tables if they don't already exist."""
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {engine.url}")
