from __future__ import annotations

from typing import TYPE_CHECKING

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Browser, Page, TimeoutError, sync_playwright

from .runtime import (
    configure_playwright_browsers_path,
    get_logger,
)

if TYPE_CHECKING:
    from .app import Credentials

LOGIN_URL = "http://10.1.1.131/srun_portal_success?ac_id=1&theme=pro"
LOGIN_SETTLE_MS = 3_000
NAVIGATION_TIMEOUT_MS = 30_000
SELECTOR_TIMEOUT_MS = 15_000
LOGOUT_TIMEOUT_MS = 3_000


def auto_login(credentials: Credentials) -> None:
    logger = get_logger()
    configure_playwright_browsers_path()

    with sync_playwright() as playwright:
        browser: Browser | None = None
        page: Page | None = None

        try:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(
                LOGIN_URL,
                wait_until="domcontentloaded",
                timeout=NAVIGATION_TIMEOUT_MS,
            )
            _logout_if_present(page)

            page.wait_for_selector("#username", timeout=SELECTOR_TIMEOUT_MS)
            page.fill("#username", credentials.student_id)
            page.wait_for_selector("#password", timeout=SELECTOR_TIMEOUT_MS)
            page.fill("#password", credentials.password)

            page.wait_for_selector("#login-account", timeout=SELECTOR_TIMEOUT_MS)
            page.click("#login-account")
            page.wait_for_timeout(LOGIN_SETTLE_MS)
            logger.info("登录完成")
        finally:
            if browser is not None:
                browser.close()


def _logout_if_present(page: Page) -> None:
    logger = get_logger()

    try:
        page.click("#logout", timeout=LOGOUT_TIMEOUT_MS)
        page.wait_for_selector(".btn-confirm", timeout=SELECTOR_TIMEOUT_MS)
        page.click(".btn-confirm")
        page.wait_for_timeout(LOGIN_SETTLE_MS)
        page.reload(wait_until="domcontentloaded", timeout=NAVIGATION_TIMEOUT_MS)
    except TimeoutError:
        return
    except PlaywrightError as exc:
        logger.debug("出现问题: %s", exc)
