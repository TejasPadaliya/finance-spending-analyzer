"""Tests for src.ingest.synthetic.generate()."""

import pandas as pd

from src.ingest.synthetic import ACCOUNTS, generate

EXPECTED_COLUMNS = {
    "transaction_id",
    "date",
    "description",
    "amount",
    "account",
    "category",
    "pending",
}


def test_returns_summary_dict(tmp_path):
    summary = generate(tmp_path)
    assert isinstance(summary["rows"], int) and summary["rows"] > 0
    assert isinstance(summary["anomalies_injected"], int)
    assert summary["anomalies_injected"] >= 1
    assert set(summary["accounts"]) == set(ACCOUNTS)


def test_writes_csv_and_parquet(tmp_path):
    generate(tmp_path)
    assert (tmp_path / "transactions.csv").exists()
    assert (tmp_path / "transactions.parquet").exists()


def test_csv_schema(tmp_path):
    generate(tmp_path)
    df = pd.read_csv(tmp_path / "transactions.csv")
    assert EXPECTED_COLUMNS == set(df.columns)


def test_sign_convention(tmp_path):
    generate(tmp_path)
    df = pd.read_csv(tmp_path / "transactions.csv")
    assert (df.loc[df["category"] == "income", "amount"] > 0).all(), (
        "income rows must have positive amounts"
    )
    assert (df.loc[df["category"] == "dining", "amount"] < 0).all(), (
        "dining rows must have negative amounts"
    )
    assert (df.loc[df["category"] == "rent", "amount"] < 0).all(), (
        "rent rows must have negative amounts"
    )


def test_date_range_spans_12_months(tmp_path):
    summary = generate(tmp_path, months=12)
    start = pd.to_datetime(summary["date_range"][0])
    end = pd.to_datetime(summary["date_range"][1])
    assert (end - start).days >= 330, "date range should span at least ~11 months"


def test_reproducibility(tmp_path):
    # uuid4 is OS-seeded, so transaction_id differs per run by design.
    # All other columns (amounts, dates, descriptions) must be identical.
    a = generate(tmp_path / "a", seed=42)
    b = generate(tmp_path / "b", seed=42)
    assert a["rows"] == b["rows"]
    cols = ["date", "description", "amount", "account", "category", "pending"]
    df_a = pd.read_csv(tmp_path / "a" / "transactions.csv")[cols]
    df_b = pd.read_csv(tmp_path / "b" / "transactions.csv")[cols]
    pd.testing.assert_frame_equal(df_a, df_b)


def test_pending_is_sparse(tmp_path):
    generate(tmp_path)
    df = pd.read_csv(tmp_path / "transactions.csv")
    pct = df["pending"].sum() / len(df)
    assert 0.01 < pct < 0.15, f"pending rate {pct:.1%} outside expected 1-15% range"
