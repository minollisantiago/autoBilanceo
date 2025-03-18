import asyncio
from pathlib import Path
from ....lib import AFIPAuthenticator, BrowserSetup, AFIPNavigator, AFIPOperator
from ....lib.services.comprobantes import (
    InvoiceInputHandler,
    select_invoice_type,
    verify_rcel_page,
    navigate_to_invoice_generator,
    fill_invoice_issuance_data_form,
    fill_recipient_form,
)

async def main():
    setup = BrowserSetup(headless=False)  # Set to false for testing
    page = await setup.setup()
    if not page:
        raise Exception("⨯ Browser setup failed")

    try:
        # Load invoice data
        invoice_template_path = Path(__file__).parent.parent.parent.parent / "data" / "invoice_testing_template.json"
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
            step_2_args = {
                "punto_venta": invoice_data["invoice"]["punto_venta"],
                "issuer_type": invoice_data["issuer"]["type"],
                "invoice_type": invoice_data["invoice"]["type"],
                "verbose": True
            }
            step_2 = await operator.execute_operation(select_invoice_type, step_2_args, verbose=True)
            if not step_2:
                print("⨯ Failed to select invoice type")
                return
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
            step_3 = await operator.execute_operation(fill_invoice_issuance_data_form, step_3_args, verbose=True)
            if not step_3:
                print("⨯ Failed to fill the invoice issuance data form")
                return
            print("✓ Successfully filled issuance data form")

            # Step 4: Fill form 2 - invoice recipient data
            step_4_args = {
                "issuer_type": invoice_data["issuer"]["type"],
                "recipient_iva_condition": invoice_data["recipient"]["iva_condition"],
                "recipient_cuit": invoice_data["recipient"]["cuit"],
                "payment_method": invoice_data["invoice"]["payment"]["method"],
                "verbose": True
            }
            step_4 = await operator.execute_operation(fill_recipient_form, step_4_args, verbose=True)
            if not step_4:
                print("⨯ Failed to fill the invoice recipient data form")
                return
            print("✓ Successfully filled recipient data form")

    finally:
        await setup.close()

def run():
    asyncio.run(main())

if __name__ == "__main__":
    run()
