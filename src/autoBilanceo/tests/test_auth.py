import asyncio
from ..lib import AFIPAuthenticator, BrowserSetup

async def main():
    setup = BrowserSetup(headless=False)  # Set to false for testing
    page = await setup.setup()

    if not page:
        raise Exception("⨯ Browser setup failed")

    try:
        auth = AFIPAuthenticator(page)
        success = await auth.authenticate(verbose=True) #Verbose set to true for testing
        if not success:
            print("⨯ Authentication failed")
            return

        print("✓ Successfully authenticated with AFIP")
        # Continue with other operations... finding services, etc
    finally:
        await setup.close()

def run():
    asyncio.run(main())

if __name__ == "__main__":
    run()
