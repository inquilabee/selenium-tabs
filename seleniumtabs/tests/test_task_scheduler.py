import time

from selenium.webdriver.common.by import By


def test_task_scheduling_with_time_website(browser):
    """Test task scheduling using a real-time website."""
    # Open a website that displays current time
    tab = browser.open("https://time.is")

    # Get initial time
    tab.find_element(By.ID, "clock").text

    # Schedule a task to check time every 2 seconds
    times_checked = []

    def check_time(tab):
        current_time = tab.find_element(By.ID, "clock").text
        times_checked.append(current_time)
        print(f"Current time: {current_time}")

    # Schedule the task
    tab.schedule_task(check_time, period=2)

    # Start task execution
    browser.execute_task(max_time=6, sleep_time=0.5)

    # Verify that we got multiple time checks
    assert times_checked, "Task should have executed at least once"

    # Verify that times are different (website is updating)
    assert len(set(times_checked)) > 1, "Times should be different as website updates"


def test_task_cancellation_with_time_website(browser):
    """Test task cancellation using a real-time website."""
    # Open a website that displays current time
    tab = browser.open("https://time.is")

    # Schedule a task to check time
    times_checked = []

    def check_time(tab):
        current_time = tab.find_element(By.ID, "clock").text
        times_checked.append(current_time)
        print(f"Current time: {current_time}")

    # Schedule the task
    tab.schedule_task(check_time, period=1)

    # Start task execution
    browser.execute_task(max_time=3, sleep_time=0.5)

    # Wait a bit
    time.sleep(2)

    # Cancel the task
    from seleniumtabs.schedule_tasks import task_scheduler

    task_scheduler.cancel_task("check_time")

    # Wait a bit more
    time.sleep(2)

    # Get final count of time checks
    final_count = len(times_checked)

    # The number of checks should be small since we cancelled the task
    assert final_count <= 4, "Task should have been cancelled and not executed many times"


def test_multiple_tasks_with_time_website(browser):
    """Test scheduling multiple tasks using a real-time website."""
    # Open a website that displays current time
    tab = browser.open("https://time.is")

    # Schedule two different tasks
    times_checked = []
    page_titles = []

    def check_time(tab):
        current_time = tab.find_element(By.ID, "clock").text
        times_checked.append(current_time)
        print(f"Current time: {current_time}")

    def check_title(tab):
        title = tab.title
        page_titles.append(title)
        print(f"Page title: {title}")

    # Schedule both tasks
    tab.schedule_task(check_time, period=2)
    tab.schedule_task(check_title, period=1)

    # Start task execution
    browser.execute_task(max_time=5, sleep_time=0.5)

    # Verify both tasks executed
    assert times_checked, "Time check task should have executed"
    assert page_titles, "Title check task should have executed"


def test_task_error_handling_with_time_website(browser):
    """Test error handling in scheduled tasks using a real-time website."""
    # Open a website that displays current time
    tab = browser.open("https://time.is")

    # Schedule a task that will raise an exception
    def failing_task(tab):
        raise Exception("This is a simulated error")

    tab.schedule_task(failing_task, period=1)

    # Start task execution - should not raise the exception
    browser.execute_task(max_time=3, sleep_time=0.5)

    # The page should still be functional
    clock = tab.find_element(By.ID, "clock")
    assert clock.is_displayed()


def test_task_execution_timing(browser):
    """Test that task execution respects the max_time parameter."""
    # Open a website that displays current time
    tab = browser.open("https://time.is")

    # Schedule a task
    times_checked = []

    def check_time(tab):
        current_time = tab.find_element(By.ID, "clock").text
        times_checked.append(current_time)
        print(f"Current time: {current_time}")

    tab.schedule_task(check_time, period=1)

    # Start task execution with max_time
    start_time = time.time()
    browser.execute_task(max_time=3, sleep_time=0.5)
    execution_time = time.time() - start_time

    # Execution time should be close to max_time
    assert 2.5 <= execution_time <= 3.5, "Task execution should respect max_time"

    # Task should have executed multiple times
    assert len(times_checked) >= 2, "Task should have executed multiple times"
