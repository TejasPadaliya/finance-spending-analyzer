"""Shared pytest fixtures."""

import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db.models import Base


@pytest.fixture()
def tmp_db_session():
    """In-memory SQLite session with all tables created."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture()
def sample_df() -> pd.DataFrame:
    """Minimal valid transaction DataFrame (2 rows)."""
    return pd.DataFrame(
        [
            {
                "transaction_id": "tx-001",
                "date": "2025-06-15",
                "description": "TIM HORTONS #4421",
                "amount": -4.50,
                "account": "CIBC Checking",
                "category": "dining",
                "pending": False,
            },
            {
                "transaction_id": "tx-002",
                "date": "2025-06-30",
                "description": "CIBC PAYROLL DEPOSIT",
                "amount": 2500.00,
                "account": "CIBC Checking",
                "category": "income",
                "pending": False,
            },
        ]
    )
