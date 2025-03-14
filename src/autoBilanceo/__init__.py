import asyncio
from .lib.auth import AFIPAuthenticator
from .lib.navigation import AFIPNavigator
from .lib.services.comprobantes import verify_rcel_page

async def main():
    auth = AFIPAuthenticator(headless=False)  # Set to True in production
    try:
        # Authentication
        success = await auth.authenticate()
        if not success:
            print("⨯ Authentication failed")
            return

        print("✓ Successfully authenticated with AFIP")

        # Navigation: mis servicios => comprobantes en linea
        if not auth.page:
            raise Exception("⨯ Browser setup failed")
        else:
            navigator = AFIPNavigator(auth.page)
            if await navigator.find_service(
                service_text="COMPROBANTES EN LÍNEA",
                service_title="rcel",
                verify_page=verify_rcel_page,
            ):
                print("✓ Successfully navigated to Comprobantes en línea")
            else:
                print("⨯ Navigation failed")

    finally:
        await auth.close()

def run():
    asyncio.run(main())

if __name__ == "__main__":
    run()
