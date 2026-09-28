"""
Capture a GIF demo of the Cinematch Streamlit app using Playwright.

Workflow:
  1. Launch app → show home/trending page
  2. Search for a movie in the selectbox
  3. Click "Get Recommendations"
  4. Show recommendation results with posters

Output: docs/demo.gif

Usage:
    streamlit run app.py --server.headless true --server.port 8501 &
    python capture_demo.py
"""

import os
import sys
import subprocess
import shutil
import tempfile
from playwright.sync_api import sync_playwright

APP_URL = "http://localhost:8501"
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(PROJECT_DIR, "docs")
OUTPUT_GIF = os.path.join(DOCS_DIR, "demo.gif")

CHROME = "/home/aminelby/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome"


def main():
    os.makedirs(DOCS_DIR, exist_ok=True)

    if not os.path.isfile(CHROME):
        print(f"ERROR: chromium not found at {CHROME}")
        sys.exit(1)

    with tempfile.TemporaryDirectory() as video_dir:
        print(f"Recording video to: {video_dir}")

        with sync_playwright() as p:
            browser = p.chromium.launch(
                executable_path=CHROME,
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"],
            )
            context = browser.new_context(
                viewport={"width": 1280, "height": 800},
                device_scale_factor=1,
                record_video_dir=video_dir,
                record_video_size={"width": 1280, "height": 800},
            )
            page = context.new_page()

            # ── Step 1: Open app ──────────────────────────────
            print("[1/5] Opening Cinematch...")
            page.goto(APP_URL, wait_until="networkidle", timeout=45000)
            # Wait for the title text to confirm Streamlit rendered
            try:
                page.wait_for_selector("text=Unlimited Movies", timeout=20000)
            except Exception:
                print("WARNING: 'Unlimited Movies' text not found, continuing...")
            page.wait_for_timeout(4000)  # Let posters load

            # Scroll down slowly to show the trending posters grid
            print("[2/5] Showing trending movies...")
            page.evaluate("window.scrollBy(0, 300)")
            page.wait_for_timeout(1500)
            page.evaluate("window.scrollBy(0, 300)")
            page.wait_for_timeout(1500)
            # Scroll back up
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(1500)

            # ── Step 2: Search for a movie ────────────────────
            print("[3/5] Searching for a movie...")
            searchbox = page.locator('input[placeholder="Type to search..."]')
            searchbox.wait_for(state="visible", timeout=10000)
            searchbox.click()
            page.wait_for_timeout(500)
            # Type slowly to show the search interaction
            searchbox.fill("The Dark Knight")
            page.wait_for_timeout(1200)
            # Click the matching option
            option = page.locator('[role="option"]').filter(has_text="The Dark Knight").first
            option.wait_for(state="visible", timeout=5000)
            option.click()
            page.wait_for_timeout(800)

            # ── Step 3: Click Get Recommendations ─────────────
            print("[4/5] Getting recommendations...")
            button = page.locator('button:has-text("Get Recommendations")')
            button.click()
            # Wait for recommendations to load (spinner → results)
            page.wait_for_timeout(1000)
            try:
                page.wait_for_selector(".movie-card-container", timeout=20000)
            except Exception:
                print("WARNING: .movie-card-container not found, continuing...")
            page.wait_for_timeout(4000)  # Let user see the results

            # Scroll to see more recommendations
            page.evaluate("window.scrollBy(0, 300)")
            page.wait_for_timeout(1500)
            page.evaluate("window.scrollBy(0, 300)")
            page.wait_for_timeout(2000)
            # Scroll back to top
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(1000)

            # ── Step 5: Close and save ────────────────────────
            print("[5/5] Saving video...")
            context.close()
            browser.close()

        # ── Convert webm to gif ───────────────────────────────
        webm_files = [f for f in os.listdir(video_dir) if f.endswith(".webm")]
        if not webm_files:
            print("ERROR: No webm video recorded!")
            sys.exit(1)

        webm_path = os.path.join(video_dir, webm_files[0])
        print(f"Video: {webm_path}")
        vid_size = os.path.getsize(webm_path)
        print(f"Size:  {vid_size / 1024 / 1024:.1f} MB")

        # Generate palette for better GIF quality
        palette_path = os.path.join(video_dir, "palette.png")
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", webm_path,
                "-vf", "fps=10,scale=960:-1:flags=lanczos,palettegen=stats_mode=diff",
                palette_path,
            ],
            check=True, capture_output=True,
        )

        # Convert to GIF
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", webm_path, "-i", palette_path,
                "-lavfi", "fps=10,scale=960:-1:flags=lanczos [x]; [x][1:v] paletteuse=dither=bayer:bayer_scale=2",
                "-loop", "0",
                OUTPUT_GIF,
            ],
            check=True, capture_output=True,
        )

    gif_size = os.path.getsize(OUTPUT_GIF)
    print(f"\nGIF saved: {OUTPUT_GIF}")
    print(f"Size:      {gif_size / 1024:.0f} KB")
    print("Done!")


if __name__ == "__main__":
    main()