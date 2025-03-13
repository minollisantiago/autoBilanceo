import os
import random
import asyncio
from dotenv import load_dotenv
from playwright.async_api import Page
from ....models.invoice_types import IssuerType
from ....models.invoice_content_services import (
    IVARate,
    create_service_invoice_line
)

async def fill_invoice_content_form(page: Page, verbose: bool = False) -> bool:
    """
    Fill the invoice content form (Step 3 of 4).

    Environment variables used:
    - ISSUER_TYPE: Type of issuer (RESPONSABLE_INSCRIPTO or MONOTRIBUTO)
    - SERVICE_CODE: 4-digit service code
    - SERVICE_CONCEPT: Description of the service
    - UNIT_PRICE: Price per unit
    - DISCOUNT_PERCENTAGE: Optional discount percentage
    - IVA_RATE: Required for RESPONSABLE_INSCRIPTO only (e.g., "21%")

    Returns:
        bool: True if form was filled successfully
    """
    try:
        load_dotenv()

        if verbose: print("Validating invoice content data...")

        # Get and validate issuer type
        try:
            issuer_type = IssuerType[os.getenv('ISSUER_TYPE', '')]
        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid issuer type: {str(e)}")

        # Get required environment variables
        service_code = os.getenv('SERVICE_CODE')
        service_concept = os.getenv('SERVICE_CONCEPT')
        unit_price = os.getenv('UNIT_PRICE')

        if not all([service_code, service_concept, unit_price]):
            raise ValueError("Missing required environment variables")

        # Get optional variables
        discount_percentage = os.getenv('DISCOUNT_PERCENTAGE')

        # Handle IVA rate for RESPONSABLE_INSCRIPTO
        iva_rate = None
        if issuer_type == IssuerType.RESPONSABLE_INSCRIPTO:
            iva_rate_str = os.getenv('IVA_RATE', '')
            if not iva_rate_str:
                raise ValueError("IVA_RATE is required for RESPONSABLE_INSCRIPTO")

            # Convert percentage string to IVARate enum (e.g., "21%" -> IVARate.VEINTIUNO)
            iva_rate_map = {
                "0%": IVARate.CERO,
                "2.5%": IVARate.DOS_CINCO,
                "5%": IVARate.CINCO,
                "10.5%": IVARate.DIEZ_CINCO,
                "21%": IVARate.VEINTIUNO,
                "27%": IVARate.VEINTISIETE
            }
            iva_rate = iva_rate_map.get(iva_rate_str)
            if iva_rate is None:
                raise ValueError(f"Invalid IVA rate: {iva_rate_str}")

        # Validate all data using our model
        invoice_line = create_service_invoice_line(
            issuer_type=issuer_type,
            service_code=service_code,
            unit_price=unit_price,
            discount_percentage=discount_percentage,
            iva_rate=iva_rate
        )

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
        if issuer_type == IssuerType.RESPONSABLE_INSCRIPTO:
            if verbose: print(f"Selecting IVA rate: {iva_rate.name}")
            iva_selector = 'select[name="detalleTipoIVA"]'
            await page.wait_for_selector(iva_selector, timeout=5000)
            await asyncio.sleep(random.uniform(0.5, 1))
            await page.select_option(iva_selector, str(iva_rate.value))
        
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
