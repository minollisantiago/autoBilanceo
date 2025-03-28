import random
import asyncio
from pathlib import Path
from typing import Optional
from playwright.async_api import Page

async def confirm_invoice_generation(
    page: Page,
    issuer_cuit: str,
    downloads_path: Optional[Path] = None,
    verbose: bool = False
) -> bool:
    """
    Confirms the invoice generation by clicking the 'Confirmar Datos...' button
    on the invoice summary page (Step 4 of 4) and downloads the generated PDF.

    Args:
        page (Page): The Playwright page instance containing the invoice summary.
        issuer_cuit (str): The CUIT number of the issuer for PDF organization.
        downloads_path (Optional[Path]): Custom path for storing downloaded PDFs.
            If provided, PDFs will be organized in CUIT-specific folders.
            If None, files will be stored in Playwright's temporary directory.
        verbose (bool): Whether to print progress messages.

    Returns:
        bool: True if invoice generation and PDF download were successful.

    Note:
        When downloads_path is not provided, PDFs are stored in Playwright's
        temporary directory and are automatically cleaned up when the browser
        session ends.
    """

    try:
        if verbose: print("Confirming invoice generation...")

        # Wait for the confirmation button to be visible and enabled
        confirm_button = await page.wait_for_selector(
            '#btngenerar',
            state='visible',
            timeout=5000
        )

        if not confirm_button:
            raise Exception("Could not find the invoice confirmation button")

        # Add a small random delay before clicking (human-like behavior)
        await asyncio.sleep(random.uniform(0.5, 1))

        # Click the confirmation button and handle the browser confirmation dialog
        #NOTE: When clicking the confirm_button, a dialog will pop up to confirm the generation.
        #NOTE: We verride confirm to always return true on this line:
        await page.evaluate("confirm = () => true;")
        await confirm_button.click()

        # Wait for AJAX call to start: "generando_comprobante" div should be visible
        await page.wait_for_selector(
            '#generando_comprobante',
            state='visible',
            timeout=5000
        )

        if verbose: print("⏳ Generating invoice...")

        # Wait for AJAX call to complete (1-1.5s) and then check results
        await asyncio.sleep(random.uniform(1, 1.5))

        # Check for success case - botones_comprobante visible and contains invoice ID
        success_div = await page.query_selector('#botones_comprobante')
        if success_div and await success_div.is_visible():
            # Try to get the invoice ID from the page
            invoice_id = await page.evaluate("idComprobante")
            if invoice_id and not await page.evaluate("isNaN(parseInt(idComprobante))"):
                if verbose: print(f"✓ Successfully generated invoice #{invoice_id} for CUIT {issuer_cuit}")

                # Handle PDF download
                if verbose: print("📄 Downloading invoice PDF...")

                # Wait for and click the print button
                print_button = await page.wait_for_selector(
                    'input[value="Imprimir..."]',
                    state='visible',
                    timeout=5000
                )
                if not print_button:
                    raise Exception("Could not find the print invoice button")
                await print_button.click()

                # Wait for the download to complete
                async with page.expect_download() as download_info:
                    download = await download_info.value
                    invoice_filename = download.suggested_filename

                    # If downloads_path is provided, save to custom location
                    if downloads_path:
                        _downloads_path = downloads_path / issuer_cuit
                        _downloads_path.mkdir(parents=True, exist_ok=True)
                        await download.save_as(_downloads_path / invoice_filename)
                        if verbose: print(f"✓ PDF saved to {_downloads_path / invoice_filename}")
                    else:
                        # Let Playwright handle it in its temporary directory
                        await download.save_as(download.suggested_filename)
                        if verbose: print(f"✓ PDF saved to temporary location: {download.suggested_filename}")
                return True

        # Check for error case
        error_div = await page.query_selector('#error_comprobante')
        if error_div and await error_div.is_visible():
            # Get the error message
            error_msg = await page.evaluate("""() => {
                const msgElement = document.getElementById('mensaje_error');
                return msgElement ? msgElement.innerText : 'Unknown error';
            }""")

            # Map common error types
            if "<!--pdferror-->" in error_msg:
                error_type = "PDF Generation Error: Invoice created but cannot be printed at this time"
            elif "<!--caeerror-->" in error_msg:
                error_type = "Authorization Code Error: Invalid invoice - could not generate authorization code"
            elif "<!--datosadicionaleserror-->" in error_msg:
                error_type = "Additional Data Error: Failed to load additional invoice data"
            else:
                error_type = f"Unknown error: {error_msg}"

            if verbose: print(f"⨯ Invoice generation failed: {error_type}")
            return False

        # If we get here, something unexpected happened
        raise Exception(f"Could not determine invoice generation status for CUIT {issuer_cuit}")

    except Exception as e:
        error_msg = f"Failed to confirm invoice generation for CUIT {issuer_cuit}: {str(e)}"
        if verbose: print(f"⨯ {error_msg}")
        return False
