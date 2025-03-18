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

    async def execute_batch_operations(
        self,
        operation_fn: Callable[[Page, Dict[str, Any]], Awaitable[bool]],
        batch_data: list[Dict[str, Any]],
        max_retries: int = 3,
        delay_between_ops: tuple[float, float] = (1.0, 2.0),
        verbose: bool = False
    ) -> list[bool]:
        """
        Execute a batch of operations sequentially with retry logic

        Args:
            operation_fn: Async function that performs the specific service operation
            batch_data: List of dictionaries containing data for each operation
            max_retries: Maximum number of retry attempts per operation
            delay_between_ops: Tuple of (min, max) seconds to wait between operations
            verbose: Whether to print detailed progress messages

        Returns:
            list[bool]: List of operation results (True for success, False for failure)
        """
        results = []

        for idx, operation_data in enumerate(batch_data):
            if verbose: print(f"\nProcessing operation {idx + 1}/{len(batch_data)}")

            # Try the operation with retries
            success = False
            for attempt in range(max_retries):
                if attempt > 0 and verbose: print(f"Retry attempt {attempt + 1}/{max_retries}")

                success = await self.execute_operation(operation_fn, operation_data, verbose=verbose)

                if success:
                    break

                # Add delay before retry
                if not success and attempt < max_retries - 1:
                    await asyncio.sleep(random.uniform(1, 2))

            results.append(success)

            # Add delay between operations
            if idx < len(batch_data) - 1:
                await asyncio.sleep(random.uniform(*delay_between_ops))

        return results

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
