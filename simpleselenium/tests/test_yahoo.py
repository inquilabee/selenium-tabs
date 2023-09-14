from simpleselenium import settings
from simpleselenium.browser import Browser

logger = settings.getLogger(__name__)

logger.info("Yahoo Test Starts")


def test_run_yahoo():
    err_msg = "Something went wrong. Report immediately."

    with Browser(name="Chrome", implicit_wait=10, headless=False) as browser:
        logger.info("Test Starts")
        yahoo_url = "https://www.yahoo.com/"
        yahoo = browser.open(yahoo_url)

        yahoo.scroll_down(times=5)
        yahoo.scroll_up(times=5)
        yahoo.scroll(times=5)

        assert yahoo.url == yahoo_url, err_msg

        # Finding/Selecting

        yahoo_anchors = sum(
            (yahoo.jq("a", element=stream) for stream in yahoo.jq(".stream-item")),
            start=[],
        )
        other_yahoo_anchors = yahoo.jquery(".stream-item a")

        logger.debug(f"yahoo_anchors: {len(yahoo_anchors)}")
        logger.debug(f"other_yahoo_anchors: {len(other_yahoo_anchors)}")

        assert len(yahoo_anchors) == len(other_yahoo_anchors), err_msg

        # Elements with text

        sports_menu = yahoo.jq.find_elements_with_text(text="Sports", selector="li", first_match=True)

        yahoo.click(sports_menu)

        yahoo.wait_for_url("https://sports.yahoo.com/")
        yahoo.wait_for_body_tag_presence_and_visibility()

        yahoo.scroll(times=3)
