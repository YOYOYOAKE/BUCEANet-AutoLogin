from __future__ import annotations

from typing import TYPE_CHECKING

from playwright.sync_api import Browser, Page, TimeoutError, sync_playwright

from .app import get_logger

if TYPE_CHECKING:
    from .app import Credentials

LOGIN_URL = "http://10.1.1.131/srun_portal_success?ac_id=1&theme=pro"
LOGIN_SETTLE_MS = 3_000
NAVIGATION_TIMEOUT_MS = 30_000
SELECTOR_TIMEOUT_MS = 15_000
CHECK_LOGGED_IN_TIMEOUT_MS = 3_000


def auto_login(credentials: Credentials) -> None:
    logger = get_logger()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(
                LOGIN_URL,
                wait_until="domcontentloaded",
                timeout=NAVIGATION_TIMEOUT_MS,
            )

            if _is_logged_in(page):
                logger.info("已登录")
                return

            page.wait_for_selector("#username", timeout=SELECTOR_TIMEOUT_MS)
            page.fill("#username", credentials.student_id)
            page.wait_for_selector("#password", timeout=SELECTOR_TIMEOUT_MS)
            page.fill("#password", credentials.password)

            page.wait_for_selector("#login-account", timeout=SELECTOR_TIMEOUT_MS)
            page.click("#login-account")
            page.wait_for_timeout(LOGIN_SETTLE_MS)
            logger.info("登录完成")
        finally:
            browser.close()


def _is_logged_in(page: Page) -> bool:
    try:
        page.wait_for_selector("#logout", timeout=CHECK_LOGGED_IN_TIMEOUT_MS)
        return True
    except TimeoutError:
        return False
