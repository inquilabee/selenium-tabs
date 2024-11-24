from seleniumtabs import Browser, Tab


def print_name(tab: Tab, name, *args, **kwargs):
    print(name, tab.domain)
    tab.scroll()
    print()


def test_task_schedule():
    with Browser(name="Chrome", implicit_wait=10, headless=False) as browser:
        google = browser.open("https://google.com")
        bing = browser.open("https://bing.com")
        duck_duck = browser.open("https://duckduckgo.com/")

        google.schedule_task(print_name, 3, "google")
        bing.schedule_task(print_name, 5, "bing")
        duck_duck.schedule_task(print_name, 10, "duck")

        browser.execute_task(max_time=60)
