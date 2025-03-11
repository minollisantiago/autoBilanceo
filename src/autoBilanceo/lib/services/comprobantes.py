import os
from playwright.async_api import Page
import asyncio
import random
from typing import Dict, Any

async def verify_rcel_page(page: Page) -> bool:
    """Verify RCEL (Comprobantes en línea) page and handle empresa selection"""
    try:
        # Handle empresa selection if present
        empresa_selector = 'input.btn_empresa'
        if await page.is_visible(empresa_selector):
            await page.wait_for_load_state('networkidle')

        # Wait for the RCEL specific elements
        await page.wait_for_selector('table#encabezado_usuario', timeout=5000)

        # Get and verify the user info matches
        user_info = await page.locator('table#encabezado_usuario td').inner_text()
        env_cuit = str(os.getenv('AFIP_CUIT', '')).replace('-', '')

        # The user info format is "CUIT - NAME"
        page_cuit = user_info.split(' - ')[0].strip()

        # Verify CUIT match and print confirmation
        cuit_matches = page_cuit == env_cuit
        if cuit_matches:
            print(f"✓ RCEL Service - CUIT verification successful: {env_cuit}")
        else:
            print(f"⨯ RCEL Service - CUIT mismatch - Page: {page_cuit}, Expected: {env_cuit}")

        return cuit_matches

    except Exception as e:
        print(f"⨯ RCEL Service verification failed: {str(e)}")
        return False

async def navigate_to_invoice_generator(page: Page, verbose: bool = False) -> bool:
    """
    Navigate to the invoice generator page by:
    1. Clicking the empresa selection button
    2. Waiting for page refresh
    3. Clicking the 'Generar Comprobantes' button

    Args:
        page: The Playwright page object
        verbose: Whether to print detailed progress messages

    Returns:
        bool: True if navigation was successful
    """
    try:
        # 1. Click the empresa selection button
        if verbose: print("Locating and clicking empresa selection button...")

        empresa_selector = 'input.btn_empresa.ui-button'
        await page.wait_for_selector(empresa_selector, timeout=5000)
        await asyncio.sleep(random.uniform(0.5, 1))
        await page.click(empresa_selector)

        # Wait for page refresh
        await page.wait_for_load_state('networkidle')

        # 2. Locate and click the 'Generar Comprobantes' button
        if verbose: print("Locating and clicking 'Generar Comprobantes' button...")

        generate_invoice_selector = 'a#btn_gen_cmp[role="button"]'
        await page.wait_for_selector(generate_invoice_selector, timeout=5000)
        await asyncio.sleep(random.uniform(0.5, 1))
        await page.click(generate_invoice_selector)

        # Wait for navigation after clicking the generate button
        await page.wait_for_load_state('networkidle')

        if verbose: print("✓ Successfully navigated to invoice generator")
        return True

    except Exception as e:
        print(f"⨯ Failed to navigate to invoice generator: {str(e)}")
        return False


async def fill_invoice_form(page: Page, form_data: Dict[str, Any]) -> bool:
    """
    Fill the invoice form with the provided data

    Args:
        page: The Playwright page object
        form_data: Dictionary containing the form field values

    Returns:
        bool: True if form was filled and submitted successfully
    """
    try:
        # Fill form fields
        for field, value in form_data.items():
            # Add human-like delays and typing
            await page.fill(f"selector_for_{field}", value)
            await asyncio.sleep(random.uniform(0.1, 0.3))

        # Submit form
        await page.click('submit_button_selector')

        # Verify submission
        return await verify_submission(page)

    except Exception as e:
        print(f"⨯ Failed to fill invoice form: {str(e)}")
        return False

async def verify_submission(page: Page) -> bool:
    """Verify that the form submission was successful"""
    try:
        # Wait for success message or confirmation element
        await page.wait_for_selector('success_message_selector', timeout=5000)
        return True
    except Exception:
        return False

