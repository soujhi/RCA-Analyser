import os
import asyncio
from dotenv import load_dotenv
from playwright.async_api import async_playwright
import anthropic

# Load environment variables
load_dotenv()

async def analyze_webpage_with_claude(url: str):
    """
    Example workflow combining Playwright web extraction and Claude AI analysis.
    """
    print(f"[Playwright] Navigating to {url}...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        
        # Extract page text content
        page_text = await page.inner_text("body")
        await browser.close()
        
    print("[Playwright] Content extracted successfully.")
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key == "your_anthropic_api_key_here":
        print("[Claude AI] ANTHROPIC_API_KEY is not set in .env. Skipping API call.")
        print(f"Extracted Text Preview (first 200 chars):\n{page_text[:200]}...")
        return

    print("[Claude AI] Sending extracted content to Claude for summary...")
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=300,
        messages=[
            {"role": "user", "content": f"Summarize the following webpage content concisely:\n\n{page_text[:3000]}"}
        ]
    )
    print("\n=== Claude AI Summary ===")
    print(response.content[0].text)

if __name__ == "__main__":
    target_url = "https://example.com"
    asyncio.run(analyze_webpage_with_claude(target_url))
