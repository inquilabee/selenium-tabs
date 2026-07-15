---
name: quality-gate
description: Runs and interprets Selenium Tabs quality checks with uv, Ruff, pytest, Bandit, pre-commit, and build. Use before commits, PRs, releases, or when the user asks to verify the package.
---

# Quality Gate

Run from the repository root.

## Fast Gate

```bash
make check-commit
make build
```

This checks formatting, lint, default tests, Bandit, and package build.

## Full Local Gate

```bash
uv sync --all-groups
uv run ruff format --check .
uv run ruff check .
uv run pytest -q
uv run pytest --cov=seleniumtabs --cov-report=term-missing
uv run bandit -c bandit.yaml -r seleniumtabs
uv build
uv run pre-commit run --all-files
```

## Integration Gate

```bash
make integration
```

Use only when live browser/network behavior matters. These tests may fail or skip when Chrome, drivers, or external sites are unavailable.

## Troubleshooting

- If `uv lock` fails, inspect dependency constraints before changing versions.
- If browser tests skip, report the Chrome/driver environment blocker instead of claiming browser coverage.
- If pre-commit reformats files, re-run the relevant gate after reviewing the diff.
- Never skip hooks or suppress findings without documenting why.
