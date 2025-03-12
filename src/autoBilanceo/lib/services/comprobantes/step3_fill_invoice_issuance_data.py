import os
import random
import asyncio
from dotenv import load_dotenv
from playwright.async_api import Page
from ....models.invoice_issuance_data import ConceptType, create_issuance_data

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

        return True

    except Exception as e:
        print(f"⨯ Failed to fill issuance data form: {str(e)}")
        return False

