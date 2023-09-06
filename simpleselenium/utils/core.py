from selenium.webdriver.common.by import By
from selenium.webdriver.remote import webelement


def find_element_by_text(element: webelement.WebElement, text):
    return element.find_element(by=By.XPATH, value=f".//*[text()='{text}']")


def find_elements_by_text(element: webelement.WebElement, text):
    return element.find_elements(by=By.XPATH, value=f".//*[text()='{text}']")


def find_parent_element(element: webelement.WebElement):
    return element.find_element(by=By.XPATH, value="..']")
