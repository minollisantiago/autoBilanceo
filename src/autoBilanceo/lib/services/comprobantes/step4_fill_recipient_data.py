import os
import random
import asyncio
from dotenv import load_dotenv
from playwright.async_api import Page
from ....models.invoice_recipient_data import (
    IVACondition,
    create_iva_condition_info,
    create_cuit_number,
)
from ....models.invoice_types import IssuerType
from ....models.invoice_payment_methods import (
    PaymentMethod,
    create_payment_method_info,
)

async def fill_recipient_data(page: Page, verbose: bool = False) -> bool:
    """
    Fill the recipient data form (Step 2 of 4).

    Environment variables used:
    - ISSUER_TYPE: Type of issuer (must be a valid IssuerType enum value)
    - RECIPIENT_IVA_CONDITION: IVA condition of the recipient
    - RECIPIENT_CUIT: CUIT number of the recipient (11 digits)
    - PAYMENT_METHOD: Payment method(s) to select

    Returns:
        bool: True if form was filled successfully
    """
    try:
        load_dotenv()

        if verbose: print("Validating recipient data...")

        # Get and validate IVA condition
        try:
            issuer_type = IssuerType[os.getenv('ISSUER_TYPE', '')]
            iva_condition = IVACondition[os.getenv('RECIPIENT_IVA_CONDITION', '')]

            # Validate IVA condition for issuer type
            iva_info = create_iva_condition_info(condition=iva_condition, issuer_type=issuer_type)
            if verbose: print(f"✓ Valid IVA condition: {iva_condition.name}")

        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid IVA condition or issuer type: {str(e)}")

        # Get and validate CUIT
        recipient_cuit = os.getenv('RECIPIENT_CUIT')
        if not recipient_cuit:
            raise ValueError("RECIPIENT_CUIT not found in environment variables")

        try:
            cuit_info = create_cuit_number(recipient_cuit)
            if verbose: print(f"✓ Valid CUIT: {cuit_info.number}")
        except ValueError as e:
            raise ValueError(f"Invalid CUIT format: {str(e)}")

        # Get and validate payment method
        payment_method_str = os.getenv('PAYMENT_METHOD')
        if not payment_method_str:
            raise ValueError("PAYMENT_METHOD not found in environment variables")

        try:
            payment_method = PaymentMethod[payment_method_str]
            payment_info = create_payment_method_info(payment_method)
            if verbose: print(f"✓ Valid payment method: {payment_method.name}")
        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid payment method: {str(e)}")

        # Fill IVA condition
        if verbose: print("Selecting IVA condition...")

        iva_selector = 'select#idivareceptor'
        await page.wait_for_selector(iva_selector, timeout=5000)
        await asyncio.sleep(random.uniform(0.5, 1))
        await page.select_option(iva_selector, str(iva_info.condition.value))

        # Fill CUIT
        if verbose: print("Filling CUIT number...")

        cuit_selector = 'input#nrodocreceptor'
        await page.wait_for_selector(cuit_selector, timeout=5000)
        await asyncio.sleep(random.uniform(0.5, 1))
        await page.fill(cuit_selector, cuit_info.number)

        # Wait for CUIT validation (the page might do some AJAX validation)
        await asyncio.sleep(random.uniform(1, 1.5))

        # Select payment method
        if verbose: print(f"Selecting payment method: {payment_method.name}")

        # Get the form ID using the model's method
        form_id = payment_info.get_form_id(payment_method)
        payment_checkbox_selector = f'input#formadepago{form_id}'
        if verbose: print(f"Using checkbox selector: {payment_checkbox_selector}")

        await page.wait_for_selector(payment_checkbox_selector, timeout=5000)
        await asyncio.sleep(random.uniform(0.5, 1))

        # Verify the value attribute matches our expected payment method value
        checkbox_value = await page.get_attribute(payment_checkbox_selector, 'value')
        if checkbox_value != str(payment_method.value):
            raise ValueError(
                f"Checkbox value mismatch for {payment_method.name}: "
                f"expected {payment_method.value}, found {checkbox_value}"
            )

        # If payment method requires card data, handle additional fields
        if payment_info.requires_card_data:
            if verbose: print("Payment method requires card data - additional handling needed")
            # TODO: Implement card data handling if needed
            pass

        await asyncio.sleep(random.uniform(0.5, 1))

        if verbose: print("Clicking [Continuar] button...")

        # Click continue button
        continue_button_selector = 'input[value="Continuar >"]'
        await page.wait_for_selector(continue_button_selector, timeout=5000)
        await page.click(continue_button_selector)

        # Wait for navigation
        await page.wait_for_load_state('networkidle')

        return True

    except Exception as e:
        print(f"⨯ Failed to fill recipient data form: {str(e)}")
        return False

