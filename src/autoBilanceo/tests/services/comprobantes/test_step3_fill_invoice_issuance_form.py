import asyncio
from pathlib import Path
from ....lib import AFIPAuthenticator, BrowserSetup, AFIPNavigator, AFIPOperator
from ....lib.services.comprobantes import (
    InvoiceInputHandler,
    select_invoice_type,
    verify_rcel_page,
    navigate_to_invoice_generator,
    fill_invoice_issuance_data_form,
)
from ....config import TEST_HEADLESS, TEST_VERBOSE

async def main():
    setup = BrowserSetup(headless=TEST_HEADLESS)  # Set to false for testing
    page = await setup.setup()
    if not page:
        raise Exception("⨯ Browser setup failed")

    try:
        # Load invoice data
        invoice_template_path = (
            Path(__file__).parent.parent.parent.parent / "data" / "invoice_testing_template.json"
        )
        input_handler = InvoiceInputHandler(invoice_template_path)

        # Get first invoice data for testing
        invoice_data = input_handler.get_invoice_data(0)
        issuer_cuit = invoice_data["issuer"]["cuit"]

        # Authentication
        auth = AFIPAuthenticator(page)
        success = await auth.authenticate(cuit=issuer_cuit, verbose=TEST_VERBOSE)
        if not success:
            raise Exception("⨯ Authentication failed")
        print("✓ Successfully authenticated with AFIP")

        # Navigation: mis servicios => comprobantes en linea
        navigator = AFIPNavigator(page)
        async with page.context.expect_page() as service_page_:
            service = await navigator.find_service(
                service_text="COMPROBANTES EN LÍNEA",
                service_title="rcel",
                verify_page=lambda p: verify_rcel_page(p, issuer_cuit),  # Pass CUIT to verify function
                verbose=TEST_VERBOSE,
            )
            if not service:
                raise Exception("⨯ Navigation to service failed")
            print("✓ Successfully navigated to Comprobantes en línea")

            # Service operations
            service_page = await service_page_.value
            operator = AFIPOperator(service_page)

            # Step 1: Navigate to invoice generation page
            step_1 = await operator.execute_operation(navigate_to_invoice_generator, {}, verbose=TEST_VERBOSE)
            if not step_1:
                raise Exception("⨯ Failed to navigate to invoice generator")
            print("✓ Successfully navigated to invoice generator")

            # Step 2: Select invoice type
            step_2_args = {
                "punto_venta": invoice_data["invoice"]["punto_venta"],
                "issuer_type": invoice_data["issuer"]["type"],
                "invoice_type": invoice_data["invoice"]["type"],
                "verbose": TEST_VERBOSE
            }
            step_2 = await operator.execute_operation(select_invoice_type, step_2_args, verbose=TEST_VERBOSE)
            if not step_2:
                raise Exception("⨯ Failed to select invoice type")
            print("✓ Successfully selected invoice type")

            # Step 3: Fill form 1 - invoice issuance data
            step_3_args = {
                "issuance_date": invoice_data["invoice"]["issuance_date"],
                "concept_type": invoice_data["invoice"]["concept_type"],
                "start_date": invoice_data["invoice"]["service_period"]["start_date"],
                "end_date": invoice_data["invoice"]["service_period"]["end_date"],
                "payment_due_date": invoice_data["invoice"]["service_period"]["payment_due_date"],
                "verbose": True
            }
            step_3 = await operator.execute_operation(fill_invoice_issuance_data_form, step_3_args, verbose=TEST_VERBOSE)
            if not step_3:
                raise Exception("⨯ Failed to fill the invoice issuance data form")
            print("✓ Successfully filled issuance data form")

    finally:
        await setup.close()

def run():
    asyncio.run(main())

if __name__ == "__main__":
    run()
