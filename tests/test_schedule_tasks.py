import schedule

from seleniumtabs.schedule_tasks import BrowserTaskScheduler


class DummyTab:
    def __init__(self):
        self.switch_count = 0

    def switch(self):
        self.switch_count += 1


def test_schedule_task_rejects_non_positive_period():
    scheduler = BrowserTaskScheduler()

    try:
        try:
            scheduler.schedule_task(DummyTab(), lambda tab: None, period=0)
        except ValueError as exc:
            assert "positive" in str(exc)
        else:
            raise AssertionError("Expected ValueError for non-positive period")
    finally:
        scheduler.cancel_all_tasks()


def test_scheduler_executes_tracks_and_cancels_tab_tasks():
    scheduler = BrowserTaskScheduler()
    tab = DummyTab()
    calls = []

    def collect(tab):
        calls.append(tab.switch_count)

    try:
        scheduler.schedule_task(tab, collect, period=0.01)

        assert scheduler.is_task_running("collect") is True

        scheduler.execute_tasks(max_time=0.05, sleep_time=0.01)

        assert calls
        assert tab.switch_count >= 1

        scheduler.cancel_tab_tasks(tab)

        assert scheduler.is_task_running("collect") is False
    finally:
        scheduler.cancel_all_tasks()


def test_cancel_task_returns_false_for_unknown_task():
    scheduler = BrowserTaskScheduler()

    assert scheduler.cancel_task("missing") is False


def test_cancel_all_tasks_leaves_unowned_schedule_jobs_intact():
    scheduler = BrowserTaskScheduler()
    tab = DummyTab()

    def scheduler_task(tab):
        return None

    def unowned_task():
        return None

    try:
        unowned_job = schedule.every(60).seconds.do(unowned_task)
        scheduler.schedule_task(tab, scheduler_task, period=60)

        scheduler.cancel_all_tasks()

        assert unowned_job in schedule.jobs
    finally:
        schedule.clear()


def test_cancel_tab_tasks_preserves_same_named_task_on_other_tabs():
    scheduler = BrowserTaskScheduler()
    first = DummyTab()
    second = DummyTab()
    calls = []

    def collect(tab):
        calls.append(tab)

    try:
        scheduler.schedule_task(first, collect, period=0.01)
        scheduler.schedule_task(second, collect, period=0.01)

        scheduler.cancel_tab_tasks(first)
        scheduler.execute_tasks(max_time=0.05, sleep_time=0.01)

        assert calls == [second]
        assert first.switch_count == 0
        assert second.switch_count == 1
        assert scheduler.is_task_running("collect") is True
    finally:
        scheduler.cancel_all_tasks()
