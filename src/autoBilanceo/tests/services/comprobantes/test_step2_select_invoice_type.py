import asyncio
from pathlib import Path
from ....lib import AFIPAuthenticator, BrowserSetup, AFIPNavigator, AFIPOperator
from ....lib.services.comprobantes import (
    InvoiceInputHandler,
    select_invoice_type,
    verify_rcel_page,
    navigate_to_invoice_generator,
)

async def main():
    setup = BrowserSetup(headless=False)  # Set to false for testing
    page = await setup.setup()
    if not page:
        raise Exception("⨯ Browser setup failed")

    try:
        # Load invoice data
        invoice_template_path = Path(__file__).parent.parent.parent.parent / "data" / "invoice_template.json"
        input_handler = InvoiceInputHandler(invoice_template_path)

        # Get first invoice data for testing
        invoice_data = input_handler.get_invoice_data(0)
        issuer_cuit = invoice_data["issuer"]["cuit"]

        # Authentication
        auth = AFIPAuthenticator(page)
        success = await auth.authenticate(cuit=issuer_cuit, verbose=True)
        if not success:
            print("⨯ Authentication failed")
            return
        print("✓ Successfully authenticated with AFIP")

        # Navigation: mis servicios => comprobantes en linea
        navigator = AFIPNavigator(page)
        async with page.context.expect_page() as service_page_:
            service = await navigator.find_service(
                service_text="COMPROBANTES EN LÍNEA",
                service_title="rcel",
                verify_page=lambda p: verify_rcel_page(p, issuer_cuit),  # Pass CUIT to verify function
                verbose=True,
            )
            if not service:
                print("⨯ Navigation to service failed")
                return
            print("✓ Successfully navigated to Comprobantes en línea")

            # Service operations
            service_page = await service_page_.value
            operator = AFIPOperator(service_page)

            # Step 1: Navigate to invoice generation page
            step_1 = await operator.execute_operation(navigate_to_invoice_generator, {}, verbose=True)
            if not step_1:
                print("⨯ Failed to navigate to invoice generator")
                return
            print("✓ Successfully navigated to invoice generator")

            # Step 2: Select invoice type
            operation_args = {
                "punto_venta": invoice_data["invoice"]["punto_venta"],
                "issuer_type": invoice_data["issuer"]["type"],
                "invoice_type": invoice_data["invoice"]["type"],
                "verbose": True
            }
            step_2 = await operator.execute_operation(select_invoice_type, operation_args, verbose=True)
            if not step_2:
                print("⨯ Failed to select invoice type")
                return
            print("✓ Successfully selected invoice type")

    finally:
        await setup.close()

def run():
    asyncio.run(main())

if __name__ == "__main__":
    run()
