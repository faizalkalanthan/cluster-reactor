from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.gui.selenium.pages.base_page import BasePage


class LoginPage(BasePage):
    HEADING = (By.XPATH, "//*[normalize-space()='Cluster Reactor']")
    SUBTITLE = (By.XPATH, "//*[contains(normalize-space(), 'Login to your tenant workspace')]")
    USERNAME_INPUT = (By.XPATH, "//input[@aria-label='Username']")
    PASSWORD_INPUT = (By.XPATH, "//input[@aria-label='Password']")
    SIGN_IN_BUTTON = (By.XPATH, "//button[normalize-space()='Sign in']")
    DEMO_HINT = (By.XPATH, "//*[contains(normalize-space(), 'Demo users: admin / writer / reader')]")

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    def wait_until_loaded(self, timeout: int = 15) -> None:
        wait = WebDriverWait(self.driver, timeout)
        wait.until(EC.visibility_of_element_located(self.HEADING))
        wait.until(EC.visibility_of_element_located(self.SUBTITLE))

    def type_username(self, username: str, timeout: int = 15) -> None:
        wait = WebDriverWait(self.driver, timeout)
        username_input = wait.until(EC.element_to_be_clickable(self.USERNAME_INPUT))
        username_input.clear()
        username_input.send_keys(username)

    def type_password(self, password: str, timeout: int = 15) -> None:
        wait = WebDriverWait(self.driver, timeout)
        password_input = wait.until(EC.element_to_be_clickable(self.PASSWORD_INPUT))
        password_input.clear()
        password_input.send_keys(password)

    def click_sign_in(self, timeout: int = 15) -> None:
        wait = WebDriverWait(self.driver, timeout)
        sign_in_button = wait.until(EC.element_to_be_clickable(self.SIGN_IN_BUTTON))
        sign_in_button.click()
