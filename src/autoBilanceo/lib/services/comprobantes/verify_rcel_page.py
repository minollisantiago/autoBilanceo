from playwright.async_api import Page

async def verify_rcel_page(page: Page, cuit: str) -> bool:
    """
    Verify RCEL (Comprobantes en línea) page and handle empresa selection

    Args:
        page: Playwright page instance
        cuit: CUIT number to verify against the page

    Returns:
        bool: True if verification succeeds
    """
    try:
        # Handle empresa selection if present
        empresa_selector = 'input.btn_empresa'
        if await page.is_visible(empresa_selector):
            await page.wait_for_load_state('networkidle')

        # Wait for the RCEL specific elements
        await page.wait_for_selector('table#encabezado_usuario', timeout=5000)

        # Get and verify the user info matches
        user_info = await page.locator('table#encabezado_usuario td').inner_text()
        expected_cuit = str(cuit).replace('-', '')

        # The user info format is "CUIT - NAME"
        page_cuit = user_info.split(' - ')[0].strip()

        # Verify CUIT match and print confirmation
        cuit_matches = page_cuit == expected_cuit
        if cuit_matches:
            print(f"✓ RCEL Service - CUIT verification successful: {expected_cuit}")
        else:
            print(f"⨯ RCEL Service - CUIT mismatch - Page: {page_cuit}, Expected: {expected_cuit}")

        return cuit_matches

    except Exception as e:
        print(f"⨯ RCEL Service verification failed: {str(e)}")
        return False
