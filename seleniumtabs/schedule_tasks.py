import time

import schedule

from seleniumtabs import settings

logger = settings.getLogger(__name__)


class BrowserTaskScheduler:
    """
    A class to manage and schedule tasks across multiple tabs in a Selenium browser.
    """

    def schedule_task(self, tab, task_func, period, *args, **kwargs):
        """
        Schedule a task to be executed on a specific tab.

        :param tab: The tab object to execute the task on.
        :param task_func: The function to execute as a task.
        :param args: Arguments for the task function.
        :param kwargs: Keyword arguments for the task function.
        """

        def task_decorator(task):
            def wrapper(tab, *args, **kwargs):
                tab.switch()
                time.sleep(0.25)
                task(tab, *args, **kwargs)

            return wrapper

        schedule.every(period).seconds.do(task_decorator(task_func), tab, *args, **kwargs)

    def execute_tasks(self, max_time=None):
        """
        Execute all scheduled tasks across their respective tabs.
        """
        start_time = time.time()

        while True:
            schedule.run_pending()
            time.sleep(1)

            if max_time and time.time() - start_time > max_time:
                break


task_scheduler = BrowserTaskScheduler()
