from __future__ import annotations

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions


def build_chrome_options() -> ChromeOptions:
    options = ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1440,1200")
    return options


def build_remote_browser(remote_url: str) -> webdriver.Remote:
    return webdriver.Remote(command_executor=remote_url, options=build_chrome_options())