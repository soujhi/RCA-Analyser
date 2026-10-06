import sys
import asyncio
from playwright.async_api import async_playwright

async def run():
    print(f"Python executable: {sys.executable}")
    print("Launching Playwright Chromium browser...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Test local content rendering
        html_content = "<html><head><title>TCS Hackathon Test</title></head><body><h1>Playwright & Python AI Ready</h1></body></html>"
        await page.set_content(html_content)
        
        title = await page.title()
        header = await page.locator("h1").text_content()
        
        print(f"Page Title: {title}")
        print(f"Header Text: {header}")
        await browser.close()
        
    print("\n[SUCCESS] Playwright environment is fully functional!")

if __name__ == "__main__":
    asyncio.run(run())
