import random
import asyncio
from playwright.async_api import Page
from ....models.invoice_types import IssuerType
from ....models.invoice_content_services import IVARate, create_service_invoice_line

async def fill_invoice_content_form(
    page: Page,
    issuer_type: str,
    service_code: str,
    service_concept: str,
    unit_price: str,
    iva_rate: str,
    discount_percentage: str = "0",
    verbose: bool = False
) -> bool:
    """
    Fill the invoice content form (Step 3 of 4).

    Args:
        page: Playwright page instance
        issuer_type: Type of issuer (RESPONSABLE_INSCRIPTO or MONOTRIBUTO)
        service_code: 4-digit service code
        service_concept: Description of the service
        unit_price: Price per unit
        iva_rate: Required for RESPONSABLE_INSCRIPTO only (e.g., "21")
        discount_percentage: Optional discount percentage (defaults to "0")
        verbose: Whether to print progress messages

    Returns:
        bool: True if form was filled successfully
    """
    try:
        if verbose: print("Validating invoice content data...")

        # Get and validate issuer type
        try:
            issuer_type_enum = IssuerType[issuer_type]
        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid issuer type: {str(e)}")

        # Handle IVA rate for RESPONSABLE_INSCRIPTO
        iva_rate_obj = None
        if issuer_type_enum == IssuerType.RESPONSABLE_INSCRIPTO:
            if not iva_rate:
                raise ValueError("IVA_RATE is required for RESPONSABLE_INSCRIPTO")

            try:
                iva_rate_obj = IVARate.from_string(iva_rate)
                if verbose: print(f"✓ Valid IVA rate: {iva_rate}%")
            except ValueError as e:
                raise ValueError(f"Invalid IVA rate: {str(e)}")

        # Validate all data using our model
        try:
            invoice_line = create_service_invoice_line(
                issuer_type=issuer_type_enum,
                service_code=service_code,
                unit_price=unit_price,
                discount_percentage=discount_percentage,
                iva_rate=iva_rate_obj
            )
        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid invoice line: {str(e)}")

        if verbose: print("✓ Valid invoice content data")

        # Fill service code
        if verbose: print(f"Filling service code: {invoice_line.service_code.code}")
        code_selector = 'input[name="detalleCodigoArticulo"]'
        await page.wait_for_selector(code_selector, timeout=5000)
        await asyncio.sleep(random.uniform(0.5, 1))
        await page.fill(code_selector, invoice_line.service_code.code)

        # Fill service concept
        if verbose: print(f"Filling service concept: {service_concept}")
        concept_selector = 'textarea[name="detalleDescripcion"]'
        await page.wait_for_selector(concept_selector, timeout=5000)
        await asyncio.sleep(random.uniform(0.5, 1))
        await page.fill(concept_selector, service_concept)

        # Fill unit price
        if verbose: print(f"Filling unit price: {invoice_line.unit_price.amount}")
        price_selector = 'input[name="detallePrecio"]'
        await page.wait_for_selector(price_selector, timeout=5000)
        await asyncio.sleep(random.uniform(0.5, 1))
        await page.fill(price_selector, str(invoice_line.unit_price.amount))

        # Fill discount if provided
        if invoice_line.discount_percentage.percentage > 0:
            if verbose: print(f"Filling discount: {invoice_line.discount_percentage.percentage}%")
            discount_selector = 'input[name="detallePorcentajeBonificacion"]'
            await page.wait_for_selector(discount_selector, timeout=5000)
            await asyncio.sleep(random.uniform(0.5, 1))
            await page.fill(discount_selector, str(invoice_line.discount_percentage.percentage))

        # Select IVA rate for RESPONSABLE_INSCRIPTO
        if issuer_type_enum == IssuerType.RESPONSABLE_INSCRIPTO and iva_rate_obj:
            if verbose: print(f"Selecting IVA rate: {iva_rate_obj.rate}%")
            iva_selector = 'select[name="detalleTipoIVA"]'
            await page.wait_for_selector(iva_selector, timeout=5000)
            await asyncio.sleep(random.uniform(0.5, 1))
            # Use the internal AFIP code for the select option
            await page.select_option(iva_selector, str(iva_rate_obj.internal_code.value))

        if verbose: print("Clicking [Continuar] button...")

        # Click continue button
        continue_button_selector = 'input[value="Continuar >"]'
        await page.wait_for_selector(continue_button_selector, timeout=5000)
        await page.click(continue_button_selector)

        # Wait for navigation
        await page.wait_for_load_state('networkidle')

        if verbose: print("✓ Successfully completed invoice content form")
        return True

    except Exception as e:
        print(f"⨯ Failed to fill invoice content form: {str(e)}")
        return False
