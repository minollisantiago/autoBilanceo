import os
import random
import asyncio
from typing import Optional
from dotenv import load_dotenv
from playwright.async_api import Page, Browser, async_playwright

class AFIPAuthenticator:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        load_dotenv()

    async def setup(self):
        """Initialize browser with anti-detection measures"""
        playwright = await async_playwright().start()
        
        # List of common user agents to rotate randomly
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/122.0.2365.66',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        ]
        
        # Common screen resolutions
        viewport_sizes = [
            {'width': 1920, 'height': 1080},
            {'width': 1366, 'height': 768},
            {'width': 1536, 'height': 864},
            {'width': 1440, 'height': 900}
        ]

        # Launch browser with enhanced anti-detection arguments
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',  # Hides automation flags
                '--disable-features=IsolateOrigins,site-per-process',  # Prevents certain fingerprinting
                '--disable-dev-shm-usage',  # Prevents memory issues in containerized environments
                '--disable-accelerated-2d-canvas',  # Reduces fingerprinting surface
                '--no-first-run',  # Skips first-run wizards
                '--no-default-browser-check',
                '--no-sandbox',  # Use carefully, only if needed
                '--disable-gpu',  # Reduces differences between systems
                f'--window-size={viewport_sizes[0]["width"]},{viewport_sizes[0]["height"]}'
            ]
        )
        
        # Create context with randomized properties
        context = await self.browser.new_context(
            viewport=random.choice(viewport_sizes),
            user_agent=random.choice(user_agents),
            locale='es-AR',  # Set Argentine Spanish locale
            timezone_id='America/Argentina/Cordoba',  # Set Córdoba timezone
            geolocation={'latitude': -31.4201, 'longitude': -64.1888},  # Córdoba coordinates
            permissions=['geolocation'],
            color_scheme='light',  # Prefer light mode
            
            # Emulate common browser features
            has_touch=False,
            is_mobile=False,
            device_scale_factor=1,
            
            # Add common HTTP headers
            extra_http_headers={
                'Accept-Language': 'es-AR,es;q=0.9,en;q=0.8',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'DNT': '1'  # Do Not Track header
            }
        )

        # Add custom JavaScript to modify browser fingerprint
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {
                        0: {type: "application/x-google-chrome-pdf"},
                        description: "Portable Document Format",
                        filename: "internal-pdf-viewer",
                        length: 1,
                        name: "Chrome PDF Plugin"
                    }
                ]
            });
        """)

        self.page = await context.new_page()
        
        # Additional page-level configurations
        await self.page.set_extra_http_headers({
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'
        })

    async def human_type(self, selector: str, text: str):
        """Simulate human-like typing with random delays"""
        if not self.page: return
        else:
            element = await self.page.wait_for_selector(selector)
            if not element: return
            else:
                for char in text:
                    await element.type(char, delay=random.uniform(100, 300))
                    await asyncio.sleep(random.uniform(0.1, 0.3))

    async def authenticate(self) -> bool:
        """Handle AFIP authentication process"""
        try:
            await self.setup()
            if not self.page:
                raise Exception("Browser setup failed")

            # Navigate to login page with random timing
            await self.page.goto('https://auth.afip.gob.ar/contribuyente_/login.xhtml')
            await asyncio.sleep(random.uniform(1, 2))

            # Enter CUIT
            await self.human_type('#F1\\:username', os.getenv('AFIP_CUIT', ''))
            await asyncio.sleep(random.uniform(0.5, 1))

            # Click continue with human-like delay
            await self.page.click('#F1\\:btnSiguiente')
            await asyncio.sleep(random.uniform(1, 2))

            # Enter password
            await self.human_type('#F1\\:password', os.getenv('AFIP_PASSWORD', ''))
            await asyncio.sleep(random.uniform(0.5, 1))

            # Click login
            await self.page.click('#F1\\:btnIngresar')

            # Wait for navigation to complete
            await self.page.wait_for_load_state('networkidle')

            # Verify successful login
            return await self._verify_login()

        except Exception as e:
            print(f"Authentication failed: {str(e)}")
            return False

    async def _verify_login(self) -> bool:
        """Verify if login was successful"""
        try:
            if not self.page: return False
            else:
                # Wait for either success or failure indicators
                await self.page.wait_for_selector('text=Servicios Habilitados', timeout=5000)
                return True
        except:
            return False

    async def close(self):
        """Clean up resources"""
        if self.browser:
            await self.browser.close()
