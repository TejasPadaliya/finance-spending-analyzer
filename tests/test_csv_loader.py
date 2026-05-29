"""Tests for src.ingest.csv_loader."""

import pytest

from src.db.models import Transaction
from src.ingest.csv_loader import load_csv, upsert_to_db


def test_load_csv_good_input(tmp_path, sample_df):
    path = tmp_path / "good.csv"
    sample_df.to_csv(path, index=False)
    df = load_csv(path)
    assert set(df.columns) == {
        "transaction_id",
        "date",
        "description",
        "amount",
        "account",
        "category",
        "pending",
    }
    assert df["amount"].dtype == float
    assert df["pending"].dtype == bool


def test_load_csv_missing_column(tmp_path, sample_df):
    bad = sample_df.drop(columns=["category"])
    path = tmp_path / "bad.csv"
    bad.to_csv(path, index=False)
    with pytest.raises(ValueError, match="missing required columns"):
        load_csv(path)


def test_load_csv_pending_coercion(tmp_path, sample_df):
    """Ensure 'True'/'False' strings from CSV round-trip to bool correctly."""
    path = tmp_path / "bool_test.csv"
    sample_df.to_csv(path, index=False)
    df = load_csv(path)
    # Both rows have pending=False in sample_df
    assert not df["pending"].any()


def test_upsert_inserts_new_rows(sample_df, tmp_db_session):
    result = upsert_to_db(sample_df, tmp_db_session)
    assert result == {"inserted": 2, "skipped": 0}
    assert tmp_db_session.query(Transaction).count() == 2


def test_upsert_is_idempotent(sample_df, tmp_db_session):
    upsert_to_db(sample_df, tmp_db_session)
    result = upsert_to_db(sample_df, tmp_db_session)
    assert result == {"inserted": 0, "skipped": 2}
    assert tmp_db_session.query(Transaction).count() == 2


def test_upsert_partial_overlap(sample_df, tmp_db_session):
    """First insert both rows; then insert one new + one duplicate."""
    upsert_to_db(sample_df, tmp_db_session)
    extra = sample_df.copy()
    extra.loc[0, "transaction_id"] = "tx-NEW"
    result = upsert_to_db(extra, tmp_db_session)
    assert result == {"inserted": 1, "skipped": 1}
    assert tmp_db_session.query(Transaction).count() == 3
