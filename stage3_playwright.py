"""
Stage 3 — Headless Browser Automation with Session Persistence
================================================================
Demonstrates:
  - Running Playwright in headless mode (no visible browser window)
  - Logging in once, saving the authenticated session (cookies + storage)
  - Reusing the saved session on future runs to skip the login step
  - Navigating directly to a protected page instead of relying on the
    homepage redirecting correctly (see README > "Lessons Learned")

Target site: https://www.saucedemo.com/ (public Playwright practice site,
safe to automate — built specifically for testing purposes).

Author: Ali Alhassis — Python Developer (Data Analysis, Web Scraping,
Streamlit Dashboards, Browser Automation)
"""

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BASE_URL = "https://www.saucedemo.com/"
INVENTORY_URL = "https://www.saucedemo.com/inventory.html"
USERNAME = "standard_user"
PASSWORD = "secret_sauce"

AUTH_STATE_FILE = Path("auth_state.json")
DEBUG_SCREENSHOT = Path("debug_screenshot.png")

NAV_TIMEOUT_MS = 15_000
ELEMENT_TIMEOUT_MS = 10_000


def login_and_save_session(playwright) -> None:
    """Perform a real login and persist the authenticated browser state to disk."""
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    try:
        print("[*] Opening login page...")
        page.goto(BASE_URL, timeout=NAV_TIMEOUT_MS, wait_until="domcontentloaded")

        page.wait_for_selector("#user-name", timeout=ELEMENT_TIMEOUT_MS)
        page.fill("#user-name", USERNAME)
        page.fill("#password", PASSWORD)
        page.click("#login-button")

        # Wait for the post-login redirect to confirm the login actually worked
        page.wait_for_url(f"{INVENTORY_URL}*", timeout=ELEMENT_TIMEOUT_MS)
        print("[+] Login successful.")

        context.storage_state(path=str(AUTH_STATE_FILE))
        print(f"[+] Session saved to {AUTH_STATE_FILE}")

    except PlaywrightTimeoutError as e:
        page.screenshot(path=str(DEBUG_SCREENSHOT))
        print(f"[!] Timeout during login: {e}")
        print(f"[!] Debug screenshot saved to {DEBUG_SCREENSHOT}")
        raise
    finally:
        context.close()
        browser.close()


def load_session_and_verify(playwright) -> None:
    """Reuse a previously saved session — no login form interaction needed."""
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(storage_state=str(AUTH_STATE_FILE))
    page = context.new_page()

    try:
        # IMPORTANT (see README "Lessons Learned"):
        # saucedemo.com's homepage ALWAYS renders the login form, regardless
        # of session state. Going straight to the protected page is what
        # actually proves the session is valid.
        print("[*] Navigating directly to the protected inventory page...")
        page.goto(INVENTORY_URL, timeout=NAV_TIMEOUT_MS, wait_until="domcontentloaded")

        page.wait_for_selector(".inventory_item", timeout=ELEMENT_TIMEOUT_MS)

        cookies = context.cookies()
        first_product = page.locator(".inventory_item_name").first.inner_text()

        print(f"[+] Cookies loaded: {len(cookies)}")
        print(f"[+] Current URL: {page.url}")
        print(f"[+] First product on page: {first_product}")

    except PlaywrightTimeoutError as e:
        page.screenshot(path=str(DEBUG_SCREENSHOT))
        print(f"[!] Session appears invalid or page did not load: {e}")
        print(f"[!] Debug screenshot saved to {DEBUG_SCREENSHOT}")
        raise
    finally:
        context.close()
        browser.close()


def main() -> None:
    with sync_playwright() as playwright:
        if AUTH_STATE_FILE.exists():
            print("[*] Existing session found — skipping login.")
            load_session_and_verify(playwright)
        else:
            print("[*] No saved session found — logging in for the first time.")
            login_and_save_session(playwright)
            load_session_and_verify(playwright)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # top-level safety net for a CLI demo
        print(f"[X] Script failed: {exc}", file=sys.stderr)
        sys.exit(1)
