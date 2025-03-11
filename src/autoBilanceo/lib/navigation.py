import random
import asyncio
from playwright.async_api import Page
from typing import Callable, Awaitable

class AFIPNavigator:
    def __init__(self, page: Page):
        self.page = page

    async def navigate_to_services(self, verbose: bool = False) -> bool:
        """Navigate to 'Mis Servicios' page after successful login"""
        try:
            print(f"Locating and navigating to Mis servicios...")
            await self.page.wait_for_load_state('networkidle')

            # Look for "Ver todos" link with exact selector
            if verbose: print(f"Looking for the 'ver todos' selector...")
            ver_todos_selector = 'a.roboto-font.regular.p-y-1.m-y-0.h4[href="/portal/app/mis-servicios"]'
            await self.page.wait_for_selector(ver_todos_selector, timeout=5000)
            await asyncio.sleep(random.uniform(0.5, 1))

            await self.page.click(ver_todos_selector)
            await self.page.wait_for_load_state('networkidle')
            print(f"✓ Sucessfully navigated to Mis servicios")
            return True
        except Exception as e:
            print(f"Navigation to mis servicios failed: {str(e)}")
            return False

    async def find_service(
        self,
        service_text: str,
        service_title: str,
        verify_page: Callable[[Page], Awaitable[bool]],
        verbose: bool = False,
    ) -> bool:
        """
        Generic service finder and navigator

        Args:
            service_text: The exact text to match in the service panel
            service_title: The title attribute of the service panel
            verify_page: Async function that verifies the destination page
        """
        try:
            if not await self.navigate_to_services(verbose=verbose):
                return False

            if verbose: print(f"Looking for the service: {service_text}")

            # Find the specific service panel
            # Service panels are all link elements with a specific title attribute associated with the service
            if verbose: print(f"Locating the service panel selector & ref button...")
            service_selector = f'a.panel.panel-default[title="{service_title}"]'
            await self.page.wait_for_selector(service_selector, timeout=5000)

            # Get the h3 text content WITHIN this specific panel
            # All service panels have an h3 element with the same tailwind classes and a specific service_text value
            if verbose: print(f"Locating and matching the service text: {service_text}")
            panel_text = await self.page.locator(f'{service_selector} h3.roboto-font.bold.h5').inner_text()

            if service_text not in panel_text:
                print(f"⨯ Service verification failed: Expected '{service_text}', found '{panel_text}'")
                return False

            print(f"✓ Found service: {service_text}")

            # Click the service panel, handle new window opening
            await asyncio.sleep(random.uniform(0.5, 1))
            async with self.page.context.expect_page() as new_page_info:
                await self.page.click(service_selector)

            # Get the new page and wait for load
            service_page = await new_page_info.value
            await service_page.wait_for_load_state('networkidle')

            # Let the verify_page() function handle service-specific verification
            if verbose: print(f"Verifying the {service_text} page content...")
            return await verify_page(service_page)

        except Exception as e:
            print(f"⨯ Failed to find or access service: {str(e)}")
            return False

