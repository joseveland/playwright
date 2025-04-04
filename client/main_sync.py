from typing import Dict

from playwright.sync_api import sync_playwright, Playwright


def run(pw: Playwright, browsers_url: str, target_url: str):
    """
    Local browser run:
        browser = pw.Xxx    # "chromium" or "firefox" or "webkit".
        running_browser = browser.launch()
        ...YOUR LOGIC HERE...
        browser.close()     # closing the browser
    ...or...
    Remote browser run, so connecting to it:
        browser = pw.Xxx    # "chromium" or "firefox" or "webkit".
        running_browser = browser.connect('ws://host:port')
        ...YOUR LOGIC HERE...
    """
    browser = pw.chromium
    running_browser = browser.connect(browsers_url)
    page = running_browser.new_page()
    page.goto(target_url)
    page.wait_for_load_state("load")
    title = page.title()
    print("Got title:", title)
    return title


def main(event: Dict, *_args, **_kwargs):
    with sync_playwright() as playwright:
        return run(playwright, event['browsers'], event['target'])


if __name__ == '__main__':
    main({
        "browsers": 'ws://localhost:8080',          # Local docker run of the playwright browsers server
        # "browsers": 'ws://18.218.228.74:8080',      # Public IP address of one ECS-task (Be careful they can re-deploy and change)
        # "browsers": 'ws://10.0.161.75:8080',        # Private IP address of one ECS-task (Be careful they can re-deploy and change)
        "target": "http://www.google.com",
    })
