from selenium.webdriver.common.by import By
from selenium.webdriver.remote import webelement


class SelectableCSS:
    """Makes an element easily selectable by CSS using .css method"""

    def __str__(self):
        return f"{self.__class__.__name__}({self.ele.get_attribute('html') or  self.ele.get_attribute('text')})"

    def __init__(self, driver_or_ele: webelement.WebElement):
        self.ele = driver_or_ele

    def css(self, selector: str) -> list[webelement.WebElement | str]:
        return [
            SelectableCSS(ele) if isinstance(ele, webelement.WebElement) else ele
            for ele in self.ele.find_elements(by=By.CSS_SELECTOR, value=selector)
        ]

    def __getattribute__(self, item):
        try:
            return super().__getattribute__(item)
        except AttributeError:
            return getattr(self.ele, item)


def select_using_jquery(driver, element: webelement.WebElement, script_code):
    return driver.execute_script(script_code, element)
