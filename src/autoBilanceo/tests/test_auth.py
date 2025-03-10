import asyncio
from ..lib.auth import AFIPAuthenticator

async def main():
    auth = AFIPAuthenticator(headless=False)  # Set to false for testing
    try:
        success = await auth.authenticate(verbose=True) #Verbose set to true for testing
        if not success:
            print("⨯ Authentication failed")
            return

        print("✓ Successfully authenticated with AFIP")
        # Continue with other operations... finding services, etc
    finally:
        await auth.close()

def run():
    asyncio.run(main())

if __name__ == "__main__":
    run()
