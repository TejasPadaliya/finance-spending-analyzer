"""Load and normalize transaction CSVs; upsert into SQLite."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

REQUIRED_COLUMNS = {
    "transaction_id",
    "date",
    "description",
    "amount",
    "account",
    "category",
    "pending",
}


def load_csv(path: Path) -> pd.DataFrame:
    """Read a transaction CSV, validate schema, coerce dtypes.

    Raises ValueError if required columns are missing.
    """
    path = Path(path)
    df = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing required columns: {sorted(missing)}")
    df = df[list(REQUIRED_COLUMNS)]
    df["transaction_id"] = df["transaction_id"].astype(str)
    df["date"] = df["date"].astype(str)
    df["description"] = df["description"].astype(str)
    df["amount"] = df["amount"].astype(float)
    df["account"] = df["account"].astype(str)
    df["category"] = df["category"].astype(str)
    # pandas reads bool columns as "True"/"False" strings — handle both
    df["pending"] = df["pending"].apply(lambda x: str(x).strip().lower() in ("true", "1", "yes"))
    return df


def upsert_to_db(df: pd.DataFrame, session: Session) -> dict[str, int]:
    """Insert new transactions into the DB, skipping existing transaction_ids.

    Returns {inserted: int, skipped: int}.
    """
    from src.db.models import Transaction

    existing_ids = {row[0] for row in session.query(Transaction.transaction_id).all()}
    inserted = skipped = 0
    for record in df.to_dict(orient="records"):
        if record["transaction_id"] in existing_ids:
            skipped += 1
        else:
            session.add(Transaction(**record))
            inserted += 1
    session.commit()
    return {"inserted": inserted, "skipped": skipped}
