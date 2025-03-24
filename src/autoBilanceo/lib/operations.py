import random
import asyncio
from playwright.async_api import Page
from typing import Callable, Awaitable, Any, Dict

class AFIPOperator:
    def __init__(self, page: Page):
        self.page = page

    async def execute_operation(
        self,
        operation_fn: Callable[..., Awaitable[bool]],
        operation_data: Dict[str, Any],
        pre_operation_delay: tuple[float, float] = (0.5, 1.0),
        verbose: bool = False
    ) -> bool:
        """
        Execute a service-specific operation with the provided data

        Args:
            operation_fn: Async function that performs the specific service operation
            operation_data: Dictionary containing the data needed for the operation
            pre_operation_delay: Tuple of (min, max) seconds to wait before operation
            verbose: Whether to print detailed progress messages

        Returns:
            bool: True if operation was successful, False otherwise
        """
        try:
            if verbose: print(f"Executing operation with data: {operation_data}")

            await asyncio.sleep(random.uniform(*pre_operation_delay))

            # Unpack the dictionary as keyword arguments
            return await operation_fn(self.page, **operation_data)

        except Exception as e:
            print(f"⨯ Operation failed: {str(e)}")
            return False

    async def verify_page_state(
        self,
        required_selectors: list[str],
        timeout: int = 5000,
        verbose: bool = False
    ) -> bool:
        """
        Verify that the page is in the expected state by checking for required elements

        Args:
            required_selectors: List of CSS selectors that should be present
            timeout: Maximum time to wait for selectors in milliseconds
            verbose: Whether to print detailed progress messages

        Returns:
            bool: True if all required elements are present, False otherwise
        """
        try:
            for selector in required_selectors:
                if verbose: print(f"Verifying presence of element: {selector}")

                await self.page.wait_for_selector(selector, timeout=timeout)

            return True

        except Exception as e:
            print(f"⨯ Page state verification failed: {str(e)}")
            return False 
