from __future__ import annotations

import os
from collections.abc import Iterator
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

import pytest

from seleniumtabs import Browser
from seleniumtabs.schedule_tasks import task_scheduler


class QuietStaticHandler(SimpleHTTPRequestHandler):
    """Static file handler that keeps pytest output focused on failures."""

    def log_message(self, format: str, *args: object) -> None:
        return None


@pytest.fixture
def fixture_server() -> Iterator[str]:
    fixtures_dir = Path(__file__).parent / "fixtures" / "pages"
    handler = partial(QuietStaticHandler, directory=str(fixtures_dir))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


@pytest.fixture
def browser() -> Iterator[Browser]:
    task_scheduler.cancel_all_tasks()
    try:
        with Browser(name="Chrome", implicit_wait=3, headless=True, full_screen=False) as browser:
            yield browser
    except Exception as exc:
        message = f"Chrome browser unavailable for Selenium tests: {exc}"
        if os.environ.get("SELENIUMTABS_FAIL_BROWSER_SKIP") == "1":
            pytest.fail(message)
        pytest.skip(message)
    finally:
        task_scheduler.cancel_all_tasks()
