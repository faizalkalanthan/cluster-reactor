from __future__ import annotations

from selenium.webdriver.remote.webdriver import WebDriver


class BasePage:
    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver

    def open(self, url: str) -> None:
        self.driver.get(url)