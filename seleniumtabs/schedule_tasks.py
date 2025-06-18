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

    Note: Tasks are executed sequentially since Selenium can only interact with one tab at a time.
    """

    def __init__(self):
        """Initialize the task scheduler"""
        self._tasks = {}  # Store task references for cancellation
        self._tab_tasks = {}  # Store tasks by tab for easy lookup
        self._running = False
        self._task_status = {}  # Track if a task is running

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
                    tab.switch()  # Switch to the correct tab
                    time.sleep(0.25)  # Small delay to ensure tab switch
                    task(tab, *args, **kwargs)
                except Exception as e:
                    logger.error(f"Error executing task {task.__name__}: {str(e)}")
                    # Don't re-raise the exception - just log it and continue

            return wrapper

        # Schedule the task and store its reference
        job = schedule.every(period).seconds.do(task_decorator(task_func), tab, *args, **kwargs)
        self._tasks[task_func.__name__] = job
        self._task_status[task_func.__name__] = True  # Mark task as running

        # Store task by tab for easy lookup
        if tab not in self._tab_tasks:
            self._tab_tasks[tab] = []
        self._tab_tasks[tab].append(task_func.__name__)

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
            self._task_status[task_name] = False  # Mark task as not running

            # Remove task from tab_tasks
            for tab_tasks in self._tab_tasks.values():
                if task_name in tab_tasks:
                    tab_tasks.remove(task_name)

            logger.info(f"Cancelled task {task_name}")
            return True
        return False

    def is_task_running(self, task_name: str) -> bool:
        """Check if a task is currently running.

        Args:
            task_name: Name of the task to check

        Returns:
            bool: True if task is running, False otherwise
        """
        return self._task_status.get(task_name, False)

    def cancel_tab_tasks(self, tab) -> None:
        """Cancel all tasks scheduled for a specific tab.

        Args:
            tab: The tab whose tasks should be cancelled
        """
        if tab in self._tab_tasks:
            for task_name in self._tab_tasks[tab]:
                self.cancel_task(task_name)
            del self._tab_tasks[tab]
            logger.info(f"Cancelled all tasks for tab {tab}")

    def cancel_all_tasks(self) -> None:
        """Cancel all scheduled tasks."""
        schedule.clear()
        self._tasks.clear()
        self._tab_tasks.clear()
        self._task_status.clear()  # Clear all task statuses
        logger.info("Cancelled all tasks")

    def execute_tasks(self, max_time: int | None = None, sleep_time: float = 1.0) -> None:
        """Execute all scheduled tasks across their respective tabs.

        Args:
            max_time: Maximum time in seconds to execute tasks. If None, no time limit is applied.
            sleep_time: Time in seconds to sleep between task checks. Defaults to 1.0 second.
                      Lower values will check for tasks more frequently but use more CPU.
                      Higher values will use less CPU but may delay task execution.

        Raises:
            ValueError: If sleep_time is not positive
        """
        if sleep_time <= 0:
            raise ValueError("sleep_time must be positive")

        self._running = True
        start_time = time.time()

        try:
            while self._running:
                try:
                    # Check if any tabs are no longer alive and cancel their tasks
                    schedule.run_pending()
                except Exception as e:
                    logger.error(f"Error during task execution: {str(e)}")
                    # Don't re-raise the exception - just log it and continue
                time.sleep(sleep_time)

                if max_time and time.time() - start_time > max_time:
                    logger.info(f"Reached maximum execution time of {max_time} seconds")
                    break
        except KeyboardInterrupt:
            logger.info("Task execution interrupted by user")
        finally:
            self._running = False

    def stop(self) -> None:
        """Stop task execution."""
        self._running = False
        logger.info("Stopping task execution")


# Create a singleton instance
task_scheduler = BrowserTaskScheduler()
