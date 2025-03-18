import random
import asyncio
from playwright.async_api import Page
from ....models.invoice_issuance_data import ConceptType, create_issuance_data

async def fill_invoice_issuance_data_form(
    page: Page,
    issuance_date: str,
    concept_type: str,
    start_date: str,
    end_date: str,
    payment_due_date: str,
    verbose: bool = False
) -> bool:
    """
    Fill the invoice issuance data form (Step 1 of 4).

    Args:
        page: Playwright page instance
        issuance_date: Date in dd/mm/yyyy format
        concept_type: Type of concept (PRODUCTOS, SERVICIOS, PRODUCTOS_Y_SERVICIOS)
        start_date: Billing period start date (dd/mm/yyyy)
        end_date: Billing period end date (dd/mm/yyyy)
        payment_due_date: Payment due date (dd/mm/yyyy)
        verbose: Whether to print progress messages

    Returns:
        bool: True if form was filled successfully
    """
    try:
        if verbose: print("Validating issuance data...")

        # Get and validate all form data using our model
        issuance_data = create_issuance_data(
            issuance_date=issuance_date,
            concept_type=ConceptType[concept_type],
            start_date=start_date,
            end_date=end_date,
            payment_due_date=payment_due_date
        )

        if not issuance_data:
            raise ValueError("Failed to create valid issuance data from provided parameters")

        if verbose: print("✓ Valid issuance data")

        # Fill issuance date
        issuance_date = issuance_data.issuance_date.format_for_afip()
        if verbose: print(f"Filling issuance date: {issuance_date}")

        date_input_selector = 'input#fc'
        await page.wait_for_selector(date_input_selector, timeout=5000)
        await asyncio.sleep(random.uniform(0.5, 1))
        await page.fill(date_input_selector, issuance_date)

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
            start_date = issuance_data.billing_period.start_date.format_for_afip()
            start_date_selector = 'input#fsd'
            await page.wait_for_selector(start_date_selector, timeout=5000)
            await asyncio.sleep(random.uniform(0.5, 1))
            await page.fill(start_date_selector, start_date)
            if verbose: print(f"Filling billing period start date: {start_date}")

            # Fill end date
            end_date = issuance_data.billing_period.end_date.format_for_afip()
            end_date_selector = 'input#fsh'
            await page.wait_for_selector(end_date_selector, timeout=5000)
            await asyncio.sleep(random.uniform(0.5, 1))
            await page.fill(end_date_selector, end_date)
            if verbose: print(f"Filling billing period end date: {end_date}")

            # Fill payment due date
            due_date = issuance_data.billing_period.payment_due_date.format_for_afip()
            due_date_selector = 'input#vencimientopago'
            await page.wait_for_selector(due_date_selector, timeout=5000)
            await asyncio.sleep(random.uniform(0.5, 1))
            await page.fill(due_date_selector, due_date)
            if verbose: print(f"Filling billing period due date: {due_date}")

            if verbose: print("✓ Successfully filled billing period")

        if verbose: print("Clicking [Continuar] button...")

        # Click continue button
        continue_button_selector = 'input[value="Continuar >"]'
        await page.wait_for_selector(continue_button_selector, timeout=5000)
        await page.click(continue_button_selector)

        # Wait for navigation
        await page.wait_for_load_state('networkidle')

        return True

    except Exception as e:
        print(f"⨯ Failed to fill issuance data form: {str(e)}")
        return False

