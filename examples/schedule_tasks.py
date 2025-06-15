"""Example demonstrating how to schedule tasks on browser tabs.

This example shows:
1. How to schedule periodic tasks on browser tabs
2. How to execute scheduled tasks with timeout
3. How to cancel tasks
4. How to handle task errors

Note: Tasks are executed sequentially since Selenium can only interact with one tab at a time.
"""

import logging
import time
from typing import Any

from seleniumtabs import Browser, settings
from seleniumtabs.schedule_tasks import task_scheduler

# Setup logging
settings.setup_logging()
logger = logging.getLogger(__name__)


def refresh_page(tab: Any, *args: Any, **kwargs: Any) -> None:
    """Example task: Refresh the current page."""
    logger.info(f"Refreshing page: {tab.url}")
    tab.driver.refresh()


def scroll_page(tab: Any, *args: Any, **kwargs: Any) -> None:
    """Example task: Scroll down the page."""
    logger.info(f"Scrolling page: {tab.url}")
    tab.scroll_down(times=1)


def check_page_title(tab: Any, *args: Any, **kwargs: Any) -> None:
    """Example task: Check and log the page title."""
    logger.info(f"Current page title: {tab.title}")


def main():
    """Main example function demonstrating task scheduling."""
    with Browser(name="Chrome", implicit_wait=10, headless=False) as browser:
        # Open some example pages
        google = browser.open("https://google.com")
        yahoo = browser.open("https://yahoo.com")

        # Schedule different tasks on different tabs
        logger.info("Scheduling tasks...")

        # Schedule page refresh every 30 seconds on Google
        google.schedule_task(refresh_page, period=30)

        # Schedule scrolling every 15 seconds on Yahoo
        yahoo.schedule_task(scroll_page, period=15)

        # Schedule title check every 10 seconds on both tabs
        google.schedule_task(check_page_title, period=10)
        yahoo.schedule_task(check_page_title, period=10)

        # Example 1: Execute tasks for 30 seconds
        logger.info("Starting task execution for 30 seconds...")
        start_time = time.time()
        browser.execute_task(max_time=30, sleep_time=0.5)  # Check tasks every 0.5 seconds
        execution_time = time.time() - start_time
        logger.info(f"Task execution completed in {execution_time:.1f} seconds")

        # Example 2: Task management
        logger.info("Managing tasks...")

        # Cancel specific tasks
        task_scheduler.cancel_task("refresh_page")
        task_scheduler.cancel_task("scroll_page")

        # Execute remaining tasks with different sleep time
        logger.info("Executing remaining tasks with 2-second sleep...")
        browser.execute_task(max_time=10, sleep_time=2.0)

        # Example 3: Error handling
        try:
            # Schedule a task that might fail
            def failing_task(tab: Any, *args: Any, **kwargs: Any) -> None:
                raise Exception("This is a simulated error")

            google.schedule_task(failing_task, period=5)
            browser.execute_task(max_time=10)
        except Exception as e:
            logger.error(f"Caught error in task execution: {e}")
        finally:
            # Clean up - cancel all tasks
            logger.info("Cleaning up - cancelling all tasks...")
            task_scheduler.cancel_all_tasks()


if __name__ == "__main__":
    main()
