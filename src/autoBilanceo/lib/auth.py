import os
import random
import asyncio
from typing import Optional
from dotenv import load_dotenv
from playwright.async_api import Page, Browser, async_playwright

class AFIPAuthenticator:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        load_dotenv()

    async def setup(self):
        """Initialize browser with appropriate settings to avoid detection"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
            ]
        )

        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        )

        self.page = await context.new_page()

    async def human_type(self, selector: str, text: str):
        """Simulate human-like typing with random delays"""
        if not self.page: return
        else:
            element = await self.page.wait_for_selector(selector)
            if not element: return
            else:
                for char in text:
                    await element.type(char, delay=random.uniform(100, 300))
                    await asyncio.sleep(random.uniform(0.1, 0.3))

    async def authenticate(self) -> bool:
        """Handle AFIP authentication process"""
        try:
            await self.setup()
            if not self.page:
                raise Exception("Browser setup failed")

            # Navigate to login page with random timing
            await self.page.goto('https://auth.afip.gob.ar/contribuyente_/login.xhtml')
            await asyncio.sleep(random.uniform(1, 2))

            # Enter CUIT
            await self.human_type('#F1\\:username', os.getenv('AFIP_CUIT', ''))
            await asyncio.sleep(random.uniform(0.5, 1))

            # Click continue with human-like delay
            await self.page.click('#F1\\:btnSiguiente')
            await asyncio.sleep(random.uniform(1, 2))

            # Enter password
            await self.human_type('#F1\\:password', os.getenv('AFIP_PASSWORD', ''))
            await asyncio.sleep(random.uniform(0.5, 1))

            # Click login
            await self.page.click('#F1\\:btnIngresar')

            # Wait for navigation to complete
            await self.page.wait_for_load_state('networkidle')

            # Verify successful login
            return await self._verify_login()

        except Exception as e:
            print(f"Authentication failed: {str(e)}")
            return False

    async def _verify_login(self) -> bool:
        """Verify if login was successful"""
        try:
            if not self.page: return False
            else:
                # Wait for either success or failure indicators
                await self.page.wait_for_selector('text=Servicios Habilitados', timeout=5000)
                return True
        except:
            return False

    async def close(self):
        """Clean up resources"""
        if self.browser:
            await self.browser.close()
