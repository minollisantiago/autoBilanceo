import asyncio
from .lib.auth import AFIPAuthenticator

async def main():
    auth = AFIPAuthenticator(headless=False)  # Set to True in production
    try:
        success = await auth.authenticate()
        if success:
            print("Successfully authenticated with AFIP")
            # Continue with other operations...
        else:
            print("Authentication failed")
    finally:
        await auth.close()

def run():
    asyncio.run(main())

if __name__ == "__main__":
    run()
