import logging
import time
from collections.abc import Callable
from typing import Any

import schedule

logger = logging.getLogger(__name__)


class BrowserTaskScheduler:
    """
    A class to manage and schedule tasks across multiple tabs in a Selenium browser.

    This class provides functionality to:
    - Schedule tasks to run on specific tabs at regular intervals
    - Execute scheduled tasks with timeout control
    - Track task execution status
    - Handle task errors gracefully
    """

    def __init__(self):
        """Initialize the task scheduler"""
        self._tasks = {}  # Store task references for cancellation
        self._running = False

    def schedule_task(self, tab, task_func: Callable[..., Any], period: int, *args: Any, **kwargs: Any) -> None:
        """Schedule a task to be executed on a specific tab.

        Args:
            tab: The tab object to execute the task on
            task_func: The function to execute as a task
            period: Time interval in seconds between task executions
            *args: Arguments for the task function
            **kwargs: Keyword arguments for the task function

        Raises:
            ValueError: If period is not positive
        """
        if period <= 0:
            raise ValueError("Task period must be positive")

        def task_decorator(task: Callable[..., Any]) -> Callable[..., Any]:
            def wrapper(tab, *args: Any, **kwargs: Any) -> None:
                try:
                    logger.debug(f"Executing task {task.__name__} on tab {tab}")
                    tab.switch()
                    time.sleep(0.25)  # Small delay to ensure tab switch
                    task(tab, *args, **kwargs)
                except Exception as e:
                    logger.error(f"Error executing task {task.__name__}: {str(e)}")
                    raise

            return wrapper

        # Schedule the task and store its reference
        job = schedule.every(period).seconds.do(task_decorator(task_func), tab, *args, **kwargs)
        self._tasks[task_func.__name__] = job
        logger.info(f"Scheduled task {task_func.__name__} to run every {period} seconds")

    def cancel_task(self, task_name: str) -> bool:
        """Cancel a scheduled task.

        Args:
            task_name: Name of the task to cancel

        Returns:
            bool: True if task was cancelled, False if task not found
        """
        if task_name in self._tasks:
            schedule.cancel_job(self._tasks[task_name])
            del self._tasks[task_name]
            logger.info(f"Cancelled task {task_name}")
            return True
        return False

    def cancel_all_tasks(self) -> None:
        """Cancel all scheduled tasks."""
        schedule.clear()
        self._tasks.clear()
        logger.info("Cancelled all tasks")

    def execute_tasks(self, max_time: int | None = None) -> None:
        """Execute all scheduled tasks across their respective tabs.

        Args:
            max_time: Maximum time in seconds to execute tasks. If None, no time limit is applied.
        """
        self._running = True
        start_time = time.time()

        try:
            while self._running:
                schedule.run_pending()
                time.sleep(1)

                if max_time and time.time() - start_time > max_time:
                    logger.info(f"Reached maximum execution time of {max_time} seconds")
                    break
        except KeyboardInterrupt:
            logger.info("Task execution interrupted by user")
        except Exception as e:
            logger.error(f"Error during task execution: {str(e)}")
            raise
        finally:
            self._running = False

    def stop(self) -> None:
        """Stop task execution."""
        self._running = False
        logger.info("Stopping task execution")


# Create a singleton instance
task_scheduler = BrowserTaskScheduler()
