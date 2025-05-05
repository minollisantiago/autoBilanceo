import random
import asyncio
from playwright.async_api import Page

async def navigate_to_invoice_generator(page: Page, company_name: str, verbose: bool = False) -> bool:
    """
    Navigate to the invoice generator page by:
    1. Clicking the empresa selection button for the specified company
    2. Waiting for page refresh
    3. Clicking the 'Generar Comprobantes' button

    Args:
        page: The Playwright page object
        company_name: The name of the company to select
        verbose: Whether to print detailed progress messages

    Returns:
        bool: True if navigation was successful
    """
    try:
        # 1. Click the empresa selection button for the specific company
        if verbose: print(f"Locating and clicking empresa selection button for {company_name}...")

        empresa_selector = f'input.btn_empresa.ui-button[value="{company_name}"]'
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

        return True

    except Exception as e:
        print(f"⨯ Failed to navigate to invoice generator: {str(e)}")
        return False
