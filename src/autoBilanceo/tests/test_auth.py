import asyncio
from ..lib import AFIPAuthenticator, BrowserSetup
from ..config import TEST_HEADLESS, TEST_VERBOSE
# Warning filters are automatically applied when importing config

async def main():
    setup = BrowserSetup(headless=TEST_HEADLESS)  # Using config value
    page = await setup.setup()
    if not page:
        raise Exception("⨯ Browser setup failed")

    try:
        issuer_cuit = "20328619548"

        auth = AFIPAuthenticator(page)
        #Make sure the cuit is at data/contribuyentes.json
        success = await auth.authenticate(cuit=issuer_cuit, verbose=TEST_VERBOSE)
        if not success:
            raise Exception("⨯ Authentication failed")
        print("✓ Successfully authenticated with AFIP")

        # Continue with other operations... finding services, etc
    finally:
        await setup.close()

def run():
    asyncio.run(main())

if __name__ == "__main__":
    run()
