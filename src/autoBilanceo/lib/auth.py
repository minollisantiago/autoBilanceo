import os
import random
import asyncio
from dotenv import load_dotenv
from playwright.async_api import Page
from .utils.human_type import human_type

class AFIPAuthenticator:
    def __init__(self, page: Page):
        self.page = page
        load_dotenv()

    async def authenticate(self, verbose: bool = False) -> bool:
        """Handle AFIP authentication process"""
        try:
            if verbose: print(f"Authenticating...")

            # Navigate to login page with random timing
            await self.page.goto('https://auth.afip.gob.ar/contribuyente_/login.xhtml')
            await asyncio.sleep(random.uniform(1, 2))

            # Enter CUIT
            if verbose: print(f"Entering Cuit...")
            await human_type(self.page, '#F1\\:username', os.getenv('AFIP_CUIT', ''))
            await asyncio.sleep(random.uniform(0.5, 1))

            # Click continue with human-like delay
            if verbose: print(f"Moving to password page...")
            await self.page.click('#F1\\:btnSiguiente')
            await asyncio.sleep(random.uniform(1, 2))

            # Enter password
            if verbose: print(f"Entering password...")
            await human_type(self.page, '#F1\\:password', os.getenv('AFIP_PASSWORD', ''))
            await asyncio.sleep(random.uniform(0.5, 1))

            # Click login
            if verbose: print(f"Clicking the login button...")
            await self.page.click('#F1\\:btnIngresar')

            # Wait for navigation to complete
            await self.page.wait_for_load_state('networkidle')

            # Verify CUIT matches
            if verbose: print(f"Verifying the CUIT number...")
            return await self.verify_CUIT()

        except Exception as e:
            print(f"Authentication failed: {str(e)}")
            return False

    async def verify_CUIT(self) -> bool:
        """Verify if login was successful by matching the logged-in CUIT with env variable"""
        try:
            if self.page:
                # Wait for CUIT element
                await self.page.wait_for_selector('.numeroCuit', timeout=5000)

                # Get the CUIT from the page and clean it
                cuit_element = await self.page.locator('.numeroCuit').inner_text()
                page_cuit = cuit_element.replace('[', '').replace(']', '').replace('-', '')

                # Get CUIT from env and ensure it's clean
                env_cuit = str(os.getenv('AFIP_CUIT', '')).replace('-', '')

                # Verify CUIT match and print confirmation
                cuit_matches = page_cuit == env_cuit
                if cuit_matches:
                    print(f"✓ CUIT verification successful: {env_cuit}")
                else:
                    print(f"⨯ CUIT mismatch - Page: {page_cuit}, Expected: {env_cuit}")

                return cuit_matches
            else:
                return False

        except Exception as e:
            print(f"⨯ CUIT verification failed: Could not find or read CUIT element: {e}")
            return False
