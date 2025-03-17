import asyncio
from ....lib import AFIPAuthenticator, BrowserSetup, AFIPNavigator, AFIPOperator
from ....lib.services.comprobantes import (
    select_invoice_type,
    verify_rcel_page,
    navigate_to_invoice_generator,
    fill_invoice_issuance_data_form,
)

async def main():
    setup = BrowserSetup(headless=False)  # Set to false for testing
    page = await setup.setup()

    if not page:
        raise Exception("⨯ Browser setup failed")

    try:
        # Authentication
        auth = AFIPAuthenticator(page)
        success = await auth.authenticate(verbose=True) #Verbose set to true for testing
        if not success:
            print("⨯ Authentication failed")
            return

        print("✓ Successfully authenticated with AFIP")

        # Navigation: mis servicios => comprobantes en linea
        if not page:
            raise Exception("⨯ Browser setup failed")
        else:
            navigator = AFIPNavigator(page)
            async with page.context.expect_page() as service_page_:
                if await navigator.find_service(
                    service_text="COMPROBANTES EN LÍNEA",
                    service_title="rcel",
                    verify_page=verify_rcel_page,
                    verbose=True,
                ):
                    print("✓ Successfully navigated to Comprobantes en línea")

                    service_page = await service_page_.value
                    operator = AFIPOperator(service_page)

                    # Navigate to invoice generation page
                    if await operator.execute_operation(navigate_to_invoice_generator, {"verbose": True}, verbose=True):
                        print("✓ Successfully navigated to invoice generator")

                        # Select invoice type
                        if await operator.execute_operation(select_invoice_type, {"verbose": True}, verbose=True):
                            print("✓ Successfully selected invoice type")

                            # Fill form 1: invoice issuance data
                            if await operator.execute_operation(fill_invoice_issuance_data_form, {"verbose": True}, verbose=True):
                                print("✓ Successfully filled issuance data form")

                    else:
                        print("⨯ Failed to navigate to invoice generator")
                else:
                    print("⨯ Navigation to service failed")

    finally:
        await setup.close()

def run():
    asyncio.run(main())

if __name__ == "__main__":
    run()
