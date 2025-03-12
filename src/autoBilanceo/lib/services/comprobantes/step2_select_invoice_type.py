import os
import random
import asyncio
from dotenv import load_dotenv
from playwright.async_api import Page
from ....models.invoice_types import InvoiceType, IssuerType, PuntoVenta, validate_invoice_type_for_issuer

async def select_invoice_type(page: Page, verbose: bool = False) -> bool:
    """
    Select the punto de venta and invoice type from the select menus.
    Validates the selections against environment variables and invoice type rules.

    Environment variables used:
    - PUNTO_VENTA: The punto de venta number (must be exactly 5 digits)
    - ISSUER_TYPE: The type of issuer (must be a valid IssuerType enum value)
    - INVOICE_TYPE: The type of invoice to generate (must be a valid InvoiceType enum value)

    Returns:
        bool: True if selections were made successfully and validated
    """
    try:
        load_dotenv()

        # Get and validate args
        if verbose: print(f"Validating punto de venta, invoice issuer and invoice type...")

        # Get punto_venta and validate using PuntoVenta model
        punto_venta_raw = os.getenv('PUNTO_VENTA')
        if not punto_venta_raw:
            raise ValueError("PUNTO_VENTA not found in environment variables")

        try:
            punto_venta = PuntoVenta.from_string(punto_venta_raw)
            # For select option we need the raw number without leading zeros
            punto_venta_clean = str(int(punto_venta.number))
            if verbose: print(f"✓ Valid punto de venta: {punto_venta.number}")
        except ValueError as e:
            raise ValueError(f"Invalid PUNTO_VENTA: {str(e)}")

        # Validate issuer and invoice types
        try:
            issuer_type = IssuerType[os.getenv('ISSUER_TYPE', '')]
            invoice_type = InvoiceType[os.getenv('INVOICE_TYPE', '')]
        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid ISSUER_TYPE or INVOICE_TYPE in environment variables: {str(e)}")

        # Validate invoice type for issuer
        if not validate_invoice_type_for_issuer(invoice_type, issuer_type):
            raise ValueError(f"Invoice type {invoice_type.name} is not valid for issuer type {issuer_type.name}")

        if verbose: print("✓ Valid invoice issuer and invoice type")

        # Fill the punto de venta and invoice type forms
        if verbose: print(f"Selecting punto de venta: {punto_venta.number}")

        # Wait for and select punto de venta
        punto_venta_selector = 'select#puntodeventa'
        await page.wait_for_selector(punto_venta_selector, timeout=5000)
        await asyncio.sleep(random.uniform(0.5, 1))

        # Select punto de venta and wait for the second select to be populated
        await page.select_option(punto_venta_selector, punto_venta_clean)
        await asyncio.sleep(random.uniform(1, 1.5))  # Wait for AJAX call to complete

        if verbose: print(f"Selecting invoice type: {invoice_type.name}")

        # Wait for and select invoice type
        invoice_type_selector = 'select#universocomprobante'
        await page.wait_for_selector(invoice_type_selector, timeout=5000)
        await asyncio.sleep(random.uniform(0.5, 1))

        # Select invoice type using its value (which is the enum value)
        await page.select_option(invoice_type_selector, str(invoice_type.value))
        await asyncio.sleep(random.uniform(0.5, 1))

        if verbose: print("Clicking [Continuar] button...")

        # Click the continue button
        continue_button_selector = 'input[type="button"][value="Continuar >"]'
        await page.wait_for_selector(continue_button_selector, timeout=5000)
        await page.click(continue_button_selector)

        # Wait for navigation after clicking continue
        await page.wait_for_load_state('networkidle')

        return True

    except Exception as e:
        print(f"⨯ Failed to select invoice type: {str(e)}")
        return False
