# Finance Spending Analyzer — Project Conventions

## What this is
An ML pipeline + Streamlit dashboard that categorizes personal transactions,
detects overspending anomalies, explains insights with SHAP, and forecasts
next month's spend. Public portfolio project. Designed for dual-mode
ingestion: CSV import (public demo, synthetic data) and Plaid integration
(personal use, real bank data, local-only deployment).

## Tech stack (do not change without asking)
- Python 3.11+, pandas, numpy, scikit-learn, SHAP, plotly, streamlit
- Plaid: plaid-python (Trial plan, personal use)
- Crypto: cryptography (Fernet for access-token storage)
- Storage: SQLite via SQLAlchemy
- Tests: pytest. Lint/format: ruff.
- Env: venv at .venv/, deps pinned in requirements.txt

## Architecture
Two ingestion adapters share one downstream pipeline:
- src/ingest/csv_loader.py   — primary, always works
- src/ingest/plaid_sync.py   — optional, real bank data, weeks 3-4
Both normalize to the canonical Transaction schema below.
src/models/, src/explain/, src/app/ are ingestion-agnostic.

## Canonical Transaction schema (do not deviate)
- transaction_id  (str, unique)
- date            (ISO YYYY-MM-DD)
- description     (str, merchant/raw description)
- amount          (float; NEGATIVE = spend/outflow, POSITIVE = income/refund)
- account         (str, friendly name e.g. "CIBC Checking", "Amex")
- category        (str, primary category; model-predicted or user-corrected)
- pending         (bool, default False)

The Plaid loader NEGATES Plaid's native sign convention so all internal
code uses the convention above. Document this clearly in plaid_sync.py.

## Hard rules
- NEVER commit anything from data/raw/. Synthetic only in data/synthetic/.
- NEVER add real API keys to code. Use .env (gitignored); template in .env.example.
- Plaid access tokens are stored encrypted (Fernet) in the local SQLite
  table `plaid_items` — never plain text, never in git.
- Real bank data runs locally only. Public deployments use Sandbox or
  synthetic CSV.
- Every public function in src/ has a docstring and a pytest test.
- Use type hints on all function signatures.
- Run `ruff check . && pytest -q` before suggesting a commit.

## Style
- Small modules, plain functions over heavy classes.
- Streamlit pages stay thin: business logic lives in src/, not in app/.
- Plotly only — no matplotlib in production code (notebooks ok).

## Git / commits
- Conventional commits: feat:, fix:, refactor:, test:, docs:, chore:
- One logical change per commit. Don't bundle unrelated edits.
- I commit and push manually. Don't run `git push`.

## My bank coverage (for Plaid integration in weeks 3-4)
- CIBC                 (main checking)        — verify Plaid OAuth coverage
- Simplii Financial    (credit card)          — verify coverage
- American Express     (credit card)          — verify coverage (usually OAuth)
- Capital One Canada   (credit card)          — verify coverage
If any aren't covered by Plaid, fall back to Flinks or CSV-only for that account.

## When in doubt
Ask. Don't invent dataset columns, model parameters, or Plaid endpoints
from thin air. Inspect data/synthetic/ first, or web-search the actual
Plaid docs before guessing API shapes.
