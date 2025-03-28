import asyncio
import warnings
from ....lib import AFIPAuthenticator, BrowserSetup, AFIPNavigator, AFIPOperator
from ....lib.services.comprobantes import verify_rcel_page, navigate_to_invoice_generator
from ....config import TEST_HEADLESS, TEST_VERBOSE
# Warning filters are automatically applied when importing config
warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed transport")
warnings.filterwarnings("ignore", message="Exception ignored.*BaseSubprocessTransport.*")

async def main():
    setup = BrowserSetup(headless=TEST_HEADLESS)  # Set to false for testing
    page = await setup.setup()
    if not page:
        raise Exception("⨯ Browser setup failed")

    try:
        issuer_cuit = "20328619548"

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

    finally:
        await setup.close()

def run():
    asyncio.run(main())

if __name__ == "__main__":
    run()
