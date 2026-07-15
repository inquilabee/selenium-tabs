---
name: review
description: Review Selenium Tabs changes for package quality, public API compatibility, Selenium behavior, tests, and release risk. Use when the user asks for a review or before publishing.
disable-model-invocation: true
---

# Review Selenium Tabs

Review all changes on the current branch or in the requested diff.

## Context

1. Read `AGENTS.md` and `.cursor/rules/`.
2. Inspect `git status --short`, branch, and diff.
3. Identify whether changes affect:
   - Public imports or method names.
   - Browser/session/tab lifecycle.
   - Scheduler globals.
   - Packaging metadata or release workflows.
   - Default vs integration tests.

## Gates

Run or verify:

```bash
make check-commit
make build
```

For live browser behavior, also run:

```bash
make integration
```

## Review Focus

- Public API compatibility and migration notes.
- Selenium cleanup and tab/session state correctness.
- Deterministic tests for default suite.
- Clear integration markers for external sites.
- No secrets, publishing tokens, or skipped hooks.
- Version, metadata, and README consistency.

## Output

Lead with findings ordered by severity. Include file references, evidence, and whether each item blocks release. If no issues are found, say so and list any skipped gates or environment limits.
