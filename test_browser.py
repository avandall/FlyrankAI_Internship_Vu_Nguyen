import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        page.on("console", lambda msg: print(f"Browser console: {msg.text}"))
        page.on("pageerror", lambda err: print(f"Browser error: {err}"))
        
        print("Navigating to localhost:8002")
        await page.goto("http://localhost:8002/")
        await page.wait_for_timeout(2000)
        
        # Test clicking tabs
        for tab in ['upload', 'library', 'review', 'metrics']:
            print(f"Clicking {tab} tab...")
            await page.evaluate(f"showTab('{tab}')")
            await page.wait_for_timeout(500)
            
            # Print html of that tab
            html = await page.evaluate(f"document.getElementById('tab-{tab}').innerHTML")
            print(f"[{tab} tab html snippet]: {html[:200].strip()}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
