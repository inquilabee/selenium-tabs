import pytest

from seleniumtabs import Browser


@pytest.fixture(scope="function")
def browser():
    """Fixture to provide a browser instance for testing."""
    with Browser(name="Chrome", implicit_wait=10, headless=False) as browser:
        yield browser
