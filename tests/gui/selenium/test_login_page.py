from __future__ import annotations

import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.gui.selenium.pages.login_page import LoginPage


pytestmark = [pytest.mark.gui, pytest.mark.selenium, pytest.mark.ui]


def test_login_page_renders_core_fields(streamlit_app_factory, selenium_remote_url: str) -> None:
    # ------------------------------------------------
    # 1. Launch browser and open app
    # ------------------------------------------------
    from tests.gui.selenium.fixtures.browser import build_remote_browser

    base_url = streamlit_app_factory()
    driver = build_remote_browser(selenium_remote_url)
    wait = WebDriverWait(driver, 15)

    try:
        # ------------------------------------------------
        # 2. Open Cluster Reactor login page
        # ------------------------------------------------
        login_page = LoginPage(driver)
        login_page.open(base_url)
        login_page.wait_until_loaded()

        # ------------------------------------------------
        # 3. Validate page content
        # ------------------------------------------------
        assert driver.find_element(*login_page.HEADING).is_displayed()
        assert driver.find_element(*login_page.SUBTITLE).is_displayed()
        assert driver.find_element(*login_page.DEMO_HINT).is_displayed()

        # ------------------------------------------------
        # 4. Validate form fields
        # ------------------------------------------------
        assert driver.find_element(*login_page.HEADING).is_displayed()
        assert driver.find_element(*login_page.USERNAME_INPUT).is_displayed()
        assert driver.find_element(*login_page.PASSWORD_INPUT).is_displayed()
        assert driver.find_element(*login_page.SIGN_IN_BUTTON).is_displayed()

        # ------------------------------------------------
        # 5. Type demo credentials
        # ------------------------------------------------
        login_page.type_username("admin")
        login_page.type_password("Admin123!")

        # ------------------------------------------------
        # 6. Verify values entered (basic interaction test)
        # ------------------------------------------------
        username_value = driver.find_element(*login_page.USERNAME_INPUT).get_attribute("value")
        password_value = driver.find_element(*login_page.PASSWORD_INPUT).get_attribute("value")
        assert username_value == "admin"
        assert password_value == "Admin123!"

        # ------------------------------------------------
        # 7. Click sign in button (UI action check)
        # ------------------------------------------------
        login_page.click_sign_in()
        wait.until(EC.visibility_of_element_located(login_page.SIGN_IN_BUTTON))
    finally:
        # ------------------------------------------------
        # 8. Close browser
        # ------------------------------------------------
        driver.quit()