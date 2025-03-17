import random
import asyncio
from playwright.async_api import Page

async def human_type(page: Page, selector: str, text: str):
    """
    Simulate human-like typing with random delays

    Args:
        page: The page to type in
        selector: The CSS selector for the input element
        text: The text to type
    """
    element = await page.wait_for_selector(selector)
    if not element: return

    for char in text:
        await element.type(char, delay=random.uniform(100, 300))
        await asyncio.sleep(random.uniform(0.1, 0.3)) 
