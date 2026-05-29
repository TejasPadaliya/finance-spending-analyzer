---
name: synthetic-data
description: Generate realistic synthetic personal transaction data for demos and tests. Use when adding sample data, fixtures, or when the user mentions "demo data", "fake transactions", "sample CSV", or needs data to test categorization, anomaly detection, or SHAP explanations.
---

# Synthetic Transaction Data Generator

Generate plausible but completely fake personal transactions for demos
and tests. Output must match the canonical Transaction schema defined
in CLAUDE.md.

## Output schema (use exactly these columns)
- transaction_id  (str, uuid4)
- date            (ISO YYYY-MM-DD, last 12 months unless told otherwise)
- description     (realistic merchant strings, e.g. "TIM HORTONS #4421",
                   "STARBUCKS YORKVILLE", "UBER TRIP 8X9K", "AMAZON.CA")
- amount          (float; NEGATIVE = spend, POSITIVE = income/refund)
- account         (str, one of: "CIBC Checking", "Simplii Visa",
                   "Amex Cobalt", "Capital One Mastercard")
- category        (str, see categories below)
- pending         (bool, ~5% pending, rest False)

## Categories to seed (weighted realistically)
groceries, dining, transit, rent, utilities, subscriptions, shopping,
entertainment, health, travel, income, transfer, other

## Realism rules
- Salary/income: 1-2 positive entries per month (~$2000-$3500), on
  consistent dates (e.g. 15th and last day).
- Rent: 1 negative entry on the 1st (~$700-$1200, consistent).
- Groceries: 4-8 entries/month, $30-$150 each.
- Dining: 8-20 entries/month, $8-$60, weekday-biased.
- Subscriptions: small recurring (Netflix, Spotify, gym, etc.) on
  consistent dates.
- Inject 1-2 anomalies per month so anomaly detection has signal:
  e.g. one dining month at 3x normal, an unusual large shopping spike.

## Output rules
- Write CSV to data/synthetic/transactions.csv (overwrite ok).
- Also write Parquet snapshot to data/synthetic/transactions.parquet.
- Seed numpy + Python `random` (seed=42) so runs are reproducible.
- Print a one-line summary (rows, date range, accounts) on completion.

## Hard rules
- Never reference any real bank's actual transaction format from prior
  contracted or co-op work.
- Never use real merchant transaction IDs or amounts from any source.
- Keep merchant names varied and realistic but invented.
