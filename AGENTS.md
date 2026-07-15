# Agents and Maintainers

This repository publishes `seleniumtabs`, a Python package that wraps Selenium with a tab-centric API.

## Start Here

- Rules: `.cursor/rules/`
- Skills: `.cursor/skills/`
- Package metadata and tool config: `pyproject.toml`
- Default tests: `tests/`
- Live browser/site tests: `tests/integration/`

## Project Boundaries

- `seleniumtabs/browser.py`: user-facing `Browser` API.
- `seleniumtabs/session.py`: WebDriver startup, options, and cleanup.
- `seleniumtabs/tabs.py`: `Tab`, `TabManager`, page actions, waits, CSS, PyQuery, JavaScript, and scheduling entry points.
- `seleniumtabs/schedule_tasks.py`: scheduler state shared by browser tabs.
- `seleniumtabs/js_scripts/`, `seleniumtabs/utils/`, `seleniumtabs/css_selectors.py`: focused helpers.

Preserve public imports from `seleniumtabs/__init__.py` unless a breaking release is intentional and documented.

## Commands

```bash
make sync
make test
make integration
make check-commit
make lint
make build
```

Default tests exclude `integration` and should not call external websites. Integration tests may require Chrome, driver downloads, network access, and live site stability.

## Package Workflow

This project uses `uv` and PEP 621 metadata.

- Add runtime dependencies in `[project].dependencies`.
- Add development tools in `[dependency-groups].dev`.
- Regenerate `uv.lock` after dependency changes.
- Build with `uv build`.
- Publish from GitHub Actions with `uv publish` and PyPI Trusted Publishing.

PyPI must be configured to trust the repository, workflow, and `pypi` environment before release publishing works.

## Agent Rules

- Read `.cursor/rules/` before substantial edits.
- Plan before multi-file changes or public API changes.
- For bug fixes, write a regression test before production changes.
- Do not commit, push, open PRs, publish, or merge unless explicitly asked.
- Never bypass hooks with `--no-verify` or `SKIP=...`.
- Verify with fresh command output before claiming work is complete.
