"""Generate realistic synthetic personal transactions for demos and tests."""

import calendar
import random
import uuid
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

ACCOUNTS = ["CIBC Checking", "Simplii Visa", "Amex Cobalt", "Capital One Mastercard"]

_MERCHANTS: dict[str, list[str]] = {
    "groceries": [
        "METRO #1204",
        "LOBLAWS STORE 4821",
        "NO FRILLS 0392",
        "SOBEYS EXPRESS",
        "FRESHCO DANFORTH",
        "FARM BOY QUEEN ST",
    ],
    "dining": [
        "TIM HORTONS #4421",
        "STARBUCKS YORKVILLE",
        "OSMOW'S SHAWARMA",
        "SUBWAY #8834",
        "MCDONALD'S BLOOR",
        "HARVEYS YONGE",
        "BURRITO BOYZ",
        "CHIPOTLE TORONTO",
        "PIZZA PIZZA #2211",
        "FRESHII KING ST",
        "POKE BOX DOWNTOWN",
    ],
    "transit": [
        "TTC PRESTO RELOAD",
        "UBER TRIP 8X9K",
        "LYFT TORONTO",
        "GO TRANSIT FARE",
    ],
    "utilities": [
        "TORONTO HYDRO",
        "ENBRIDGE GAS",
        "ROGERS COMM",
        "BELL CANADA INTERNET",
    ],
    "subscriptions": [
        "NETFLIX.COM",
        "SPOTIFY CA",
        "GOODLIFE FITNESS",
        "AMAZON PRIME CA",
        "APPLE.COM/BILL",
    ],
    "shopping": [
        "AMAZON.CA",
        "BEST BUY #0921",
        "INDIGO BOOKS",
        "H&M QUEEN WEST",
        "UNIQLO TORONTO",
        "IKEA NORTH YORK",
        "WINNERS YONGE",
        "DOLLARAMA #0447",
    ],
    "entertainment": [
        "CINEPLEX ODEON",
        "TICKETMASTER CA",
        "STEAM GAMES",
        "APPLE APP STORE",
    ],
    "health": [
        "SHOPPERS DRUG MART",
        "REXALL PHARMACY",
        "SDM PHARMACY #0821",
        "PHYSIOPLUS CLINIC",
    ],
}


def _tx(d: date, desc: str, amount: float, account: str, category: str) -> dict:
    return {
        "transaction_id": str(uuid.uuid4()),
        "date": d.isoformat(),
        "description": desc,
        "amount": round(amount, 2),
        "account": account,
        "category": category,
        "pending": False,
    }


def generate(out_dir: Path, seed: int = 42, months: int = 12) -> dict:
    """Generate synthetic transactions and write CSV + Parquet to out_dir.

    Returns {rows, date_range, accounts, anomalies_injected}.
    Amounts follow CLAUDE.md sign convention: negative = spend, positive = income/refund.
    """
    rng = np.random.default_rng(seed)
    random.seed(seed)

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Build the list of (year, month) tuples for the last `months` calendar months
    today = date.today()
    cur_year, cur_month = today.year, today.month
    month_list: list[tuple[int, int]] = []
    y, m = cur_year, cur_month
    for _ in range(months):
        m -= 1
        if m == 0:
            m = 12
            y -= 1
        month_list.append((y, m))
    month_list.reverse()  # chronological order

    # Fixed consistent amounts (seeded so reproducible)
    rent = round(float(rng.uniform(700, 1200)), 2)
    salary_main = round(float(rng.uniform(2000, 3500)), 2)
    salary_top = round(float(rng.uniform(500, 1000)), 2)

    # Fixed subscription day/amount pairs
    subs = [
        ("NETFLIX.COM", round(float(rng.uniform(14, 20)), 2), 12),
        ("SPOTIFY CA", round(float(rng.uniform(8, 11)), 2), 5),
        ("GOODLIFE FITNESS", round(float(rng.uniform(40, 60)), 2), 1),
        ("AMAZON PRIME CA", round(float(rng.uniform(8, 10)), 2), 20),
    ]

    # Decide anomaly months ahead of time (seeded)
    n_months = len(month_list)
    anomaly_dining_months = set(random.sample(range(n_months), k=max(1, n_months // 4)))
    anomaly_shopping_months = set(random.sample(range(n_months), k=max(1, n_months // 6)))

    rows: list[dict] = []
    anomalies_injected = 0

    for idx, (year, month) in enumerate(month_list):
        last_day = calendar.monthrange(year, month)[1]

        def d(day: int) -> date:
            return date(year, month, min(day, last_day))

        # Income (positive)
        rows.append(_tx(d(15), "CIBC PAYROLL DEPOSIT", salary_main, "CIBC Checking", "income"))
        rows.append(_tx(d(last_day), "CIBC PAYROLL DEPOSIT", salary_top, "CIBC Checking", "income"))

        # Rent (negative, 1st)
        rows.append(_tx(d(1), "INTERAC E-TFR RENT", -rent, "CIBC Checking", "rent"))

        # Utilities (~70% of months)
        if random.random() < 0.7:
            rows.append(
                _tx(
                    d(random.randint(5, 25)),
                    random.choice(_MERCHANTS["utilities"]),
                    -round(float(rng.uniform(60, 180)), 2),
                    "CIBC Checking",
                    "utilities",
                )
            )

        # Subscriptions (fixed day each month)
        for desc, amt, day in subs:
            rows.append(_tx(d(day), desc, -amt, "Amex Cobalt", "subscriptions"))

        # Groceries (4-8/month)
        for _ in range(int(rng.integers(4, 9))):
            rows.append(
                _tx(
                    d(random.randint(1, last_day)),
                    random.choice(_MERCHANTS["groceries"]),
                    -round(float(rng.uniform(30, 150)), 2),
                    random.choice(["CIBC Checking", "Simplii Visa"]),
                    "groceries",
                )
            )

        # Dining (8-20/month; anomaly = 3x count)
        n_dining = int(rng.integers(8, 21))
        if idx in anomaly_dining_months:
            n_dining *= 3
            anomalies_injected += 1
        for _ in range(n_dining):
            rows.append(
                _tx(
                    d(random.randint(1, last_day)),
                    random.choice(_MERCHANTS["dining"]),
                    -round(float(rng.uniform(8, 60)), 2),
                    random.choice(["Amex Cobalt", "Simplii Visa"]),
                    "dining",
                )
            )

        # Shopping (1-4/month; anomaly = large one-off spike)
        if idx in anomaly_shopping_months:
            rows.append(
                _tx(
                    d(random.randint(1, last_day)),
                    random.choice(_MERCHANTS["shopping"]),
                    -round(float(rng.uniform(300, 800)), 2),
                    "Capital One Mastercard",
                    "shopping",
                )
            )
            anomalies_injected += 1
        for _ in range(int(rng.integers(1, 5))):
            rows.append(
                _tx(
                    d(random.randint(1, last_day)),
                    random.choice(_MERCHANTS["shopping"]),
                    -round(float(rng.uniform(15, 150)), 2),
                    random.choice(["Capital One Mastercard", "Amex Cobalt"]),
                    "shopping",
                )
            )

        # Transit (2-6/month)
        for _ in range(int(rng.integers(2, 7))):
            rows.append(
                _tx(
                    d(random.randint(1, last_day)),
                    random.choice(_MERCHANTS["transit"]),
                    -round(float(rng.uniform(3, 25)), 2),
                    "CIBC Checking",
                    "transit",
                )
            )

        # Entertainment (0-3/month)
        for _ in range(int(rng.integers(0, 4))):
            rows.append(
                _tx(
                    d(random.randint(1, last_day)),
                    random.choice(_MERCHANTS["entertainment"]),
                    -round(float(rng.uniform(10, 50)), 2),
                    "Amex Cobalt",
                    "entertainment",
                )
            )

        # Health (0-2/month)
        for _ in range(int(rng.integers(0, 3))):
            rows.append(
                _tx(
                    d(random.randint(1, last_day)),
                    random.choice(_MERCHANTS["health"]),
                    -round(float(rng.uniform(10, 80)), 2),
                    "Simplii Visa",
                    "health",
                )
            )

    df = pd.DataFrame(rows)

    # Apply ~5% pending flag (separate seed so main amounts stay reproducible)
    pending_rng = np.random.default_rng(seed + 1)
    df["pending"] = pending_rng.random(len(df)) < 0.05

    df = df.sort_values("date").reset_index(drop=True)

    df.to_csv(out_dir / "transactions.csv", index=False)
    df.to_parquet(out_dir / "transactions.parquet", index=False)

    return {
        "rows": len(df),
        "date_range": (df["date"].min(), df["date"].max()),
        "accounts": sorted(df["account"].unique().tolist()),
        "anomalies_injected": anomalies_injected,
    }
