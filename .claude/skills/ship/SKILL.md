---
name: ship
description: Pre-commit verification workflow. Use when the user says "ready to commit", "ship it", "let's push", or wants to verify the project is in a clean state before a git commit.
---

# Pre-commit checklist

Run these in order. Stop and report at the first failure — do not
auto-fix unless step 1 or 2 specifies it.

1. `ruff check . --fix`          — lint and auto-fix safe issues
2. `ruff format .`               — format
3. `pytest -q`                   — all tests pass (fail = stop here)
4. Verify no files under data/raw/ are staged.
5. Verify .env is NOT staged. If it is, unstage it and warn loudly.
6. `git status`                  — show what changed.
7. `git diff --cached --stat`    — summary of staged changes.

8. Suggest a Conventional Commits-style message based on the staged diff:
   feat: <short summary>     for new features
   fix: <short summary>      for bug fixes
   refactor: <short summary> for refactors with no behavior change
   test: <short summary>     for test-only changes
   docs: <short summary>     for docs/README changes
   chore: <short summary>    for tooling, deps, config

## Hard rules
- Do NOT run `git commit` or `git push` automatically. Show me the
  suggested command for me to run.
- If pytest fails, do not propose a commit message. Report the failure.
- If .env or anything from data/raw/ was staged, refuse to suggest a
  commit and tell me what to unstage.
