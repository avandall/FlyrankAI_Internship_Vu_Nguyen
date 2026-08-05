import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            print("Navigating to http://127.0.0.1:8001...")
            await page.goto('http://127.0.0.1:8001')
            print("Taking screenshot...")
            await page.screenshot(path='/home/avandall/.gemini/antigravity-ide/brain/feab2293-b274-4244-85d4-108b2d21c34e/ai_image_ui.png', full_page=True)
            print("Screenshot saved to artifacts as ai_image_ui.png")
            content = await page.content()
            if "AI Image" in content:
                print("Page loaded successfully and looks like the right app.")
            else:
                print("Page loaded but might not be the correct app.")
        except Exception as e:
            print(f"Error navigating: {e}")
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
