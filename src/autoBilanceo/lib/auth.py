import random
import asyncio
import json
from pathlib import Path
from playwright.async_api import Page
from .utils.human_type import human_type
from ..models.cuit import create_cuit_number

class AFIPAuthenticator:
    def __init__(self, page: Page):
        self.page = page
        self._load_credentials()

    def _load_credentials(self) -> None:
        """Load credentials from contribuyentes.json file"""
        cred_path = Path(__file__).parent.parent / "data" / "contribuyentes.json"
        if not cred_path.exists():
            raise FileNotFoundError(f"Credentials file not found: {cred_path}")

        with open(cred_path, 'r') as f:
            self.credentials = json.load(f)

    async def authenticate(self, cuit: str, verbose: bool = False) -> bool:
        """
        Handle AFIP authentication process

        Args:
            cuit: The CUIT number to authenticate with
            verbose: Whether to print progress messages

        Raises:
            ValueError: If the CUIT format is invalid
        """
        try:
            if verbose: print(f"Authenticating...")

            # Validate CUIT format
            try:
                validated_cuit = create_cuit_number(cuit)
                cuit = validated_cuit.number
            except ValueError as e:
                print(f"⨯ Authentication failed: Invalid CUIT format - {str(e)}")
                return False

            # Get password for this CUIT
            if cuit not in self.credentials:
                raise KeyError(f"No credentials found for CUIT: {cuit}")
            password = self.credentials[cuit]

            # Navigate to login page with random timing
            await self.page.goto('https://auth.afip.gob.ar/contribuyente_/login.xhtml')
            await asyncio.sleep(random.uniform(1, 2))

            # Enter CUIT
            if verbose: print(f"Entering Cuit...")
            await human_type(self.page, '#F1\\:username', cuit)
            await asyncio.sleep(random.uniform(0.5, 1))

            # Click continue with human-like delay
            if verbose: print(f"Moving to password page...")
            await self.page.click('#F1\\:btnSiguiente')
            await asyncio.sleep(random.uniform(1, 2))

            # Enter password
            if verbose: print(f"Entering password...")
            await human_type(self.page, '#F1\\:password', password)
            await asyncio.sleep(random.uniform(0.5, 1))

            # Click login
            if verbose: print(f"Clicking the login button...")
            await self.page.click('#F1\\:btnIngresar')

            # Wait for navigation to complete
            await self.page.wait_for_load_state('networkidle')

            # Verify CUIT matches using the validated CUIT
            if verbose: print(f"Verifying the CUIT number...")
            return await self.verify_CUIT(cuit)

        except Exception as e:
            print(f"Authentication failed: {str(e)}")
            return False

    async def verify_CUIT(self, expected_cuit: str) -> bool:
        """
        Verify if login was successful by matching the logged-in CUIT

        Args:
            expected_cuit: The CUIT number to verify against (already validated)
        """
        try:
            if self.page:
                # Wait for CUIT element
                await self.page.wait_for_selector('.numeroCuit', timeout=5000)

                # Get the CUIT from the page and clean it
                cuit_element = await self.page.locator('.numeroCuit').inner_text()
                page_cuit = cuit_element.replace('[', '').replace(']', '').replace('-', '')

                try:
                    # Validate both CUITs using the model
                    page_cuit_validated = create_cuit_number(page_cuit)
                    expected_cuit_validated = create_cuit_number(expected_cuit)

                    # Verify CUIT match and print confirmation
                    cuit_matches = page_cuit_validated.number == expected_cuit_validated.number
                    if cuit_matches:
                        print(f"✓ CUIT verification successful: {expected_cuit}")
                    else:
                        print(f"⨯ CUIT mismatch - Page: {page_cuit}, Expected: {expected_cuit}")

                    return cuit_matches

                except ValueError as e:
                    print(f"⨯ CUIT verification failed: Invalid CUIT format - {str(e)}")
                    return False
            else:
                return False

        except Exception as e:
            print(f"⨯ CUIT verification failed: Could not find or read CUIT element: {e}")
            return False
