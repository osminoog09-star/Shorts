#!/usr/bin/env python3
"""Server-side *public page* browser compatibility probe for M1lash.

No logins, saved cookies, proxies, stealth patches, anti-bot solving, film
downloads or stream extraction. Only reports coarse booleans.
"""
from __future__ import annotations
import json
from playwright.sync_api import sync_playwright, Error as BrowserError, TimeoutError

PAGE_URL = "https://rezka.ag/films/drama/54016-oppengeymer-2023-latest.html"


def main() -> None:
    summary = {
        "browser_launched": False, "http_code": None,
        "film_heading_present": False, "challenge_present": False,
        "download_control_present": False, "media_downloaded": False,
    }
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            summary["browser_launched"] = True
            context = browser.new_context(accept_downloads=False, locale="ru-RU")
            page = context.new_page()

            # Never fetch playback media; this is a page compatibility probe only.
            page.route("**/*", lambda route: route.abort()
                       if route.request.resource_type == "media" else route.continue_())
            response = page.goto(PAGE_URL, wait_until="domcontentloaded", timeout=35000)
            summary["http_code"] = response.status if response else None
            page.wait_for_timeout(2000)
            summary["film_heading_present"] = page.locator(
                "h1[itemprop='name'], h1.b-post__title"
            ).count() > 0
            text = page.locator("body").inner_text(timeout=10000).lower()[:8000]
            summary["challenge_present"] = any(x in text for x in (
                "checking your browser", "just a moment",
                "подтвердите, что вы человек", "проверка браузера", "captcha",
                "ddos-guard", "anubis"
            ))
            summary["download_control_present"] = page.get_by_role(
                "button", name="Скачать", exact=True
            ).count() > 0 or page.get_by_role(
                "link", name="Скачать", exact=True
            ).count() > 0
            context.close()
            browser.close()
    except (BrowserError, TimeoutError, OSError):
        summary["browser_error"] = True
    # No page content, URLs with query parameters, cookies, stream data, or secrets.
    print("public_server_browser_probe:", json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
