# Test Coverage

## Strategy

The default test suite must be deterministic. Tests under `tests/` use local HTML fixtures served from `tests/fixtures/pages/` and are selected by:

```bash
make test
```

Live browser and external-website tests are kept under `tests/integration/` and marked with `@pytest.mark.integration`. Run them only when Chrome, network access, and live site stability are part of the acceptance criteria:

```bash
make integration
```

## Covered in the Default Suite

- `Session` cleanup is idempotent when driver initialization fails.
- `Browser` can open, switch, query, and close local tabs.
- `Tab.css()` and chained `SelectableCSS.css()` work against stable local markup.
- `Tab.find_element()`, `get_attribute()`, `run_js()`, and `pyquery` work on local fixtures.
- Scroll helpers run against a tall local page.
- Scheduled tab tasks execute and can be cancelled.

Browser-dependent default tests skip with a clear reason when Chrome or a driver is unavailable. Pure tests should still run in that environment.

## Integration Coverage

Integration tests preserve live checks for:

- Google/Yahoo/Bing/DuckDuckGo tab workflows.
- Yahoo selector and PyQuery behavior.
- `time.is` task scheduling behavior.

These tests are intentionally excluded from the default gate because live websites change without warning.

## Next Priorities

1. Add pure unit tests for URL parsing, wait-duration calculation, and scheduler validation.
1. Add local-fixture tests for wait helpers, staleness, invisibility, and URL waits.
1. Add local-fixture tests for click fallbacks and element geometry helpers.
1. Increase coverage threshold after the above tests land.
