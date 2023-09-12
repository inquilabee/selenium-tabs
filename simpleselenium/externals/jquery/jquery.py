import contextlib
import time

from selenium import webdriver
from selenium.webdriver.remote import webelement

from simpleselenium import settings
from simpleselenium.externals.jquery import jquery_scripts

logger = settings.getLogger(__name__)


class BrowserJQuery:
    """Jquery access for tabs"""

    def __init__(self, driver: webdriver.Chrome | webdriver.Firefox):
        self.driver = driver

        self.ensure_jquery()

    def __call__(self, *args, **kwargs):
        return self.find(*args, **kwargs)

    def ensure_jquery(self):
        return not self.is_jquery_injected and self.inject_jquery()

    def execute(self, script, *args):
        """Run JavaScript on the page"""

        return self.driver.execute_script(script, *args)

    def query(self, script: str, element: webelement.WebElement, *args):
        # TODO: Allow multiple elements as input and check (using regex?) that passed elements are wrapped inside $

        logger.info(f"Executing script : {script} on element: {element}")
        return self.execute(script, element, *args)

    @property
    def document(self):
        return self.execute("""return $(document.documentElement)""")

    @property
    def page_html(self) -> str:
        # https://stackoverflow.com/a/982742/8414030

        return self.execute(jquery_scripts.PAGE_HTML)

    def inject_jquery(self, by: str = "file", wait: int = 5) -> bool:
        """
        SO: https://stackoverflow.com/a/57947790/8414030
        """
        logger.info("Jquery being injected.")

        self._inject_jquery_file(wait=wait) if by == "file" else self._inject_jquery_cdn(wait=wait)

        return self.is_jquery_injected

    def _inject_jquery_cdn(self, wait: int = 2):
        self.driver.execute_script(jquery_scripts.JQUERY_INJECTION)

        time.sleep(wait)

    def _inject_jquery_file(self, wait: int = 5):
        with open(settings.JQUERY_INJECTION_FILE) as f:
            self.execute(f.read())

        time.sleep(wait)

    @property
    def is_jquery_injected(self) -> bool:
        with contextlib.suppress(Exception):
            self.execute(jquery_scripts.JQUERY_INJECTION_CHECK)
            return True

        return False

    @staticmethod
    def _prepare_result(result, first: bool):
        if isinstance(result, list):
            if first:
                return result[0] if result else None
            return result

        return result

    def find(
        self, selector: str, element: webelement.WebElement = None, *, first_match: bool = False
    ) -> list[webelement.WebElement] | webelement.WebElement | None:
        """Find elements using the given element or entire dom based on selector"""

        first_match = first_match or selector.startswith("#")
        element = element or self.document
        method = ".first()" if first_match else ""

        return self._prepare_result(
            self.query(
                script=f"""return $(arguments[0]).find("{selector}"){method};""",
                element=element,
            ),
            first=first_match,
        )

    def find_elements_with_text(
        self, text: str, selector: str = "*", element: webelement.WebElement = None, *, first_match: bool = False
    ) -> list[webelement.WebElement] | webelement.WebElement | None:
        """Find all elements with given texts"""

        method = ".first()" if first_match else ""

        return self._prepare_result(
            self.query(
                script=f"""
                            return $(arguments[0]).find("{selector}:contains('{text}')"){method};
                        """,
                element=element or self.document,
            ),
            first=first_match,
        )

    def find_closest_ancestor(self, selector: str, element: webelement.WebElement) -> webelement.WebElement | None:
        """Find the closest ancestor with given selector properties"""

        return self._prepare_result(
            self.query(script=f"""return $(arguments[0]).closest('{selector}')""", element=element), first=True
        )

    def has_class(self, element: webelement.WebElement, class_name: str) -> bool:
        return self.query(
            script=f"""
                  return $(arguments[0]).hasClass('{class_name}')
                """,
            element=element,
        )

    def parent(self, element: webelement.WebElement) -> webelement.WebElement:
        return self.query(
            script="""
                  return $(arguments[0]).parent()')
                """,
            element=element,
        )

    def parents(self, element: webelement.WebElement) -> list[webelement.WebElement]:
        return self.query(
            script="""
                  return $(arguments[0]).parents()')
                """,
            element=element,
        )
