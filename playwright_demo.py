"""Playwright demo for Cinematch Movie Recommendation System."""

import os
import sys
from playwright.sync_api import sync_playwright

PROJECT_DIR = "/home/aminelby/Movie-Recommendation-Project"
DOCS_DIR = os.path.join(PROJECT_DIR, "docs")
os.makedirs(DOCS_DIR, exist_ok=True)

APP_URL = "http://localhost:8501"


def find_chrome():
    candidates = [
        os.path.expanduser("~/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome"),
        os.path.expanduser("~/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome"),
        os.path.expanduser("~/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome"),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    return None


def main():
    chrome_exe = find_chrome()
    if not chrome_exe:
        print("ERROR: Could not find chromium binary.")
        sys.exit(1)

    print(f"Using chromium: {chrome_exe}")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=chrome_exe,
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"],
        )
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=1,
        )
        page = context.new_page()

        # Step 1: Open app
        print("[1/5] Opening Cinematch app...")
        page.goto(APP_URL, wait_until="networkidle", timeout=30000)
        page.wait_for_selector("text=Unlimited Movies", timeout=15000)
        page.wait_for_timeout(3000)
        page.screenshot(path=os.path.join(DOCS_DIR, "demo-01-home.png"), full_page=False)
        print("       Saved: docs/demo-01-home.png")

        # Step 2: Search for Avatar
        print("[2/5] Searching for 'Avatar'...")
        searchbox = page.locator('input[placeholder="Type to search..."]')
        searchbox.wait_for(state="visible", timeout=10000)
        searchbox.click()
        page.wait_for_timeout(800)
        searchbox.fill("Avatar")
        page.wait_for_timeout(1500)
        avatar_option = page.locator('[role="option"]').filter(has_text="Avatar").first
        avatar_option.click()
        page.wait_for_timeout(500)
        page.screenshot(path=os.path.join(DOCS_DIR, "demo-02-selected.png"), full_page=False)
        print("       Saved: docs/demo-02-selected.png")

        # Step 3: Click Get Recommendations
        print("[3/5] Clicking 'Get Recommendations'...")
        button = page.locator('button:has-text("Get Recommendations")')
        button.wait_for(state="visible", timeout=5000)
        button.click()
        page.wait_for_timeout(5000)

        # Step 4: Verify recommendations
        print("[4/5] Verifying recommendations...")
        page.wait_for_selector(".movie-card-container", timeout=15000)
        page.wait_for_timeout(2000)
        page.screenshot(path=os.path.join(DOCS_DIR, "demo-03-recommendations.png"), full_page=True)
        print("       Saved: docs/demo-03-recommendations.png")

        # Step 5: Final hero screenshot
        print("[5/5] Capturing final viewport...")
        page.screenshot(path=os.path.join(DOCS_DIR, "demo-hero.png"), full_page=False)
        print("       Saved: docs/demo-hero.png")

        browser.close()
        print("\nDemo completed! Screenshots in docs/")
        for f in sorted(os.listdir(DOCS_DIR)):
            if f.startswith("demo-"):
                fpath = os.path.join(DOCS_DIR, f)
                size_kb = os.path.getsize(fpath) / 1024
                print(f"  docs/{f} ({size_kb:.0f} KB)")


if __name__ == "__main__":
    main()