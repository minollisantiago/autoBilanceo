import asyncio
from ..lib import AFIPAuthenticator, BrowserSetup

async def main():
    setup = BrowserSetup(headless=False)  # Set to false for testing
    page = await setup.setup()
    if not page:
        raise Exception("⨯ Browser setup failed")

    try:
        issuer_cuit = "20328619548"

        auth = AFIPAuthenticator(page)
        #Make sure the cuit is at data/contribuyentes.json
        success = await auth.authenticate(cuit=issuer_cuit, verbose=True)
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
