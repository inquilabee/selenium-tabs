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
