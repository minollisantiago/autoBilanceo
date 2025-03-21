import random
import asyncio
from playwright.async_api import Page
from ....models.invoice_types import IssuerType
from ....models.invoice_payment_methods import PaymentMethod, create_payment_method_info
from ....models.invoice_recipient_data import IVACondition, create_iva_condition_info, create_cuit_number

async def fill_recipient_form(
    page: Page,
    issuer_type: str,
    recipient_iva_condition: str,
    recipient_cuit: str,
    payment_method: str,
    verbose: bool = False
) -> bool:
    """
    Fill the recipient data form (Step 2 of 4).

    Args:
        page: Playwright page instance
        issuer_type: Type of issuer (must be a valid IssuerType enum value)
        recipient_iva_condition: IVA condition of the recipient
        recipient_cuit: CUIT number of the recipient (11 digits, optional for CONSUMIDOR_FINAL)
        payment_method: Payment method to select
        verbose: Whether to print progress messages

    Returns:
        bool: True if form was filled successfully
    """
    try:
        if verbose: print("Validating recipient data...")

        # Get and validate IVA condition
        try:
            issuer_type_enum = IssuerType[issuer_type]
            iva_condition = IVACondition[recipient_iva_condition]

            # Validate IVA condition for issuer type
            iva_info = create_iva_condition_info(condition=iva_condition, issuer_type=issuer_type_enum)
            if verbose: print(f"✓ Valid IVA condition: {iva_condition.name}")

        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid IVA condition or issuer type: {str(e)}")

        # Validate CUIT
        cuit_info = None
        if iva_condition != IVACondition.CONSUMIDOR_FINAL:
            try:
                if not recipient_cuit:
                    raise ValueError("CUIT is required for non CONSUMIDOR_FINAL recipients")
                cuit_info = create_cuit_number(recipient_cuit)
                if verbose: print(f"✓ Valid CUIT: {cuit_info.number}")
            except ValueError as e:
                raise ValueError(f"Invalid CUIT format: {str(e)}")

        # Validate payment method
        try:
            payment_method_enum = PaymentMethod[payment_method]
            payment_info = create_payment_method_info(payment_method_enum)
            if verbose: print(f"✓ Valid payment method: {payment_method_enum.name}")
        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid payment method: {str(e)}")

        # Fill IVA condition
        if verbose: print("Selecting IVA condition...")

        iva_selector = 'select#idivareceptor'
        await page.wait_for_selector(iva_selector, timeout=5000)
        await asyncio.sleep(random.uniform(0.5, 1))
        await page.select_option(iva_selector, str(iva_info.condition.value))

        # Fill CUIT only for non CONSUMIDOR_FINAL recipients
        if cuit_info:
            if verbose: print("Filling CUIT number...")

            cuit_selector = 'input#nrodocreceptor'
            await page.wait_for_selector(cuit_selector, timeout=5000)
            await asyncio.sleep(random.uniform(0.5, 1))
            await page.fill(cuit_selector, cuit_info.number)

            # Wait for CUIT validation (the page might do some AJAX validation)
            await asyncio.sleep(random.uniform(1, 1.5))

        # Select payment method
        if verbose: print(f"Selecting payment method: {payment_method_enum.name}")

        payment_checkbox_selector = f'input[name="formaDePago"][value="{payment_method_enum.value}"]'
        if verbose: print(f"Using checkbox selector: {payment_checkbox_selector}")

        await page.wait_for_selector(payment_checkbox_selector, timeout=5000)
        await asyncio.sleep(random.uniform(0.5, 1))

        # Check if the checkbox is already checked - Fix the JavaScript selector string
        is_checked = await page.evaluate(f"document.querySelector('{payment_checkbox_selector}').checked")
        if not is_checked:
            await page.check(payment_checkbox_selector)

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

