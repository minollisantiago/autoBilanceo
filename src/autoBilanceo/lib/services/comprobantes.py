import os
import random
import asyncio
from typing import Dict, Any
from dotenv import load_dotenv
from playwright.async_api import Page
from ...models.invoice_issuance_data import ConceptType, create_issuance_data
from ...models.invoice_types import InvoiceType, IssuerType, PuntoVenta, validate_invoice_type_for_issuer

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

        return True

    except Exception as e:
        print(f"⨯ Failed to navigate to invoice generator: {str(e)}")
        return False

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

async def fill_invoice_issuance_data(page: Page, verbose: bool = False) -> bool:
    """
    Fill the invoice issuance data form (Step 1 of 4).

    Environment variables used:
    - ISSUANCE_DATE: Date in dd/mm/yyyy format
    - CONCEPT_TYPE: Type of concept (PRODUCTOS, SERVICIOS, PRODUCTOS_Y_SERVICIOS)
    - START_DATE: Optional billing period start date (dd/mm/yyyy)
    - END_DATE: Optional billing period end date (dd/mm/yyyy)
    - PAYMENT_DUE_DATE: Optional payment due date (dd/mm/yyyy)

    Returns:
        bool: True if form was filled successfully
    """
    try:
        load_dotenv()

        if verbose: print("Validating issuance data...")

        # Get and validate all form data using our model
        issuance_data = create_issuance_data(
            issuance_date=os.getenv('ISSUANCE_DATE', ''),
            concept_type=ConceptType[os.getenv('CONCEPT_TYPE', '')],
            start_date=os.getenv('START_DATE'),
            end_date=os.getenv('END_DATE'),
            payment_due_date=os.getenv('PAYMENT_DUE_DATE')
        )

        if not issuance_data:
            raise ValueError("Failed to create valid issuance data from environment variables")

        if verbose: print("✓ Valid issuance data")

        # Fill issuance date
        if verbose: print(f"Filling issuance date: {issuance_data.issuance_date.format_for_afip()}")

        date_input_selector = 'input#fc'
        await page.wait_for_selector(date_input_selector, timeout=5000)
        await asyncio.sleep(random.uniform(0.5, 1))
        await page.fill(date_input_selector, issuance_data.issuance_date.format_for_afip())

        # Select concept type
        if verbose: print(f"Selecting concept type: {issuance_data.concept_type.name}")

        concept_selector = 'select#idconcepto'
        await page.wait_for_selector(concept_selector, timeout=5000)
        await asyncio.sleep(random.uniform(0.5, 1))
        await page.select_option(concept_selector, str(issuance_data.concept_type.value))

        # If concept includes services, fill billing period
        if issuance_data.billing_period:
            if verbose: print("Filling billing period dates...")

            # Fill start date
            start_date_selector = 'input#fsd'
            await page.wait_for_selector(start_date_selector, timeout=5000)
            await asyncio.sleep(random.uniform(0.5, 1))
            await page.fill(
                start_date_selector,
                issuance_data.billing_period.start_date.format_for_afip()
            )

            # Fill end date
            end_date_selector = 'input#fsh'
            await page.wait_for_selector(end_date_selector, timeout=5000)
            await asyncio.sleep(random.uniform(0.5, 1))
            await page.fill(
                end_date_selector,
                issuance_data.billing_period.end_date.format_for_afip())

            # Fill payment due date
            due_date_selector = 'input#vencimientopago'
            await page.wait_for_selector(due_date_selector, timeout=5000)
            await asyncio.sleep(random.uniform(0.5, 1))
            await page.fill(
                due_date_selector,
                issuance_data.billing_period.payment_due_date.format_for_afip()
            )

            if verbose: print("✓ Successfully filled billing period")

        if verbose: print("Clicking [Continuar] button...")

        # Click continue button
        continue_button_selector = 'input[value="Continuar >"]'
        await page.wait_for_selector(continue_button_selector, timeout=5000)
        await page.click(continue_button_selector)

        # Wait for navigation
        await page.wait_for_load_state('networkidle')

        if verbose: print("✓ Successfully completed issuance data form")
        return True

    except Exception as e:
        print(f"⨯ Failed to fill issuance data form: {str(e)}")
        return False

