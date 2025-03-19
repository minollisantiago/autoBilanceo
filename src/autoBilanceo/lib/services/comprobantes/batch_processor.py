import asyncio
from typing import List, Dict, Any
from ....lib import BrowserSetup, AFIPAuthenticator, AFIPNavigator, AFIPOperator
from .verify_rcel_page import verify_rcel_page
from .step1_nav_to_invoice_generator import navigate_to_invoice_generator
from .step2_select_invoice_type import select_invoice_type
from .step3_fill_invoice_issuance_data_form import fill_invoice_issuance_data_form
from .step4_fill_recipient_form import fill_recipient_form
from .step5_fill_invoice_content_form import fill_invoice_content_form

class InvoiceBatchProcessor:
    def __init__(
        self,
        max_concurrent: int = 3,
        delay_between_batches: int = 2,
        headless: bool = True,
        verbose: bool = False
    ):
        """
        Initialize the batch processor.

        Args:
            max_concurrent: Maximum number of concurrent browser instances
            verbose: Whether to print progress messages
        """
        self.max_concurrent = max_concurrent
        self.delay_between_batches = delay_between_batches
        self.headless = headless
        self.verbose = verbose
        self.results: List[Dict[str, Any]] = []

    async def process_single_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single invoice through the complete workflow.

        Args:
            invoice_data: Dictionary containing all invoice data

        Returns:
            Dictionary containing the processing result
        """
        result = {
            "issuer_cuit": invoice_data["issuer"]["cuit"],
            "invoice_type": invoice_data["invoice"]["type"],
            "status": "failed",
            "error": None
        }

        try:
            # Setup browser
            setup = BrowserSetup(headless=self.headless)
            page = await setup.setup()
            if not page:
                raise Exception("⨯ Browser setup failed")

            try:
                # Authentication
                auth = AFIPAuthenticator(page)
                if not await auth.authenticate(cuit=invoice_data["issuer"]["cuit"], verbose=self.verbose):
                    raise Exception("Authentication failed")

                # Navigation to service
                navigator = AFIPNavigator(page)
                async with page.context.expect_page() as service_page_:
                    if not await navigator.find_service(
                        service_text="COMPROBANTES EN LÍNEA",
                        service_title="rcel",
                        verify_page=lambda p: verify_rcel_page(p, invoice_data["issuer"]["cuit"]),
                        verbose=self.verbose
                    ):
                        raise Exception("Service navigation failed")

                    # Service operations
                    service_page = await service_page_.value
                    operator = AFIPOperator(service_page)

                    # Step 1: Navigate to invoice generation page
                    step_1_args = {"verbose": self.verbose}
                    if not await operator.execute_operation(navigate_to_invoice_generator, step_1_args, verbose=self.verbose):
                        raise Exception("Navigation to invoice generator failed")

                    # Step 2: Select invoice type
                    step2_args = {
                        "punto_venta": invoice_data["invoice"]["punto_venta"],
                        "issuer_type": invoice_data["issuer"]["type"],
                        "invoice_type": invoice_data["invoice"]["type"],
                        "verbose": self.verbose
                    }
                    if not await operator.execute_operation(select_invoice_type, step2_args, verbose=self.verbose):
                        raise Exception("Invoice type selection failed")

                    # Step 3: Fill issuance data
                    step3_args = {
                        "issuance_date": invoice_data["invoice"]["issuance_date"],
                        "concept_type": invoice_data["invoice"]["concept_type"],
                        "start_date": invoice_data["invoice"]["service_period"]["start_date"],
                        "end_date": invoice_data["invoice"]["service_period"]["end_date"],
                        "payment_due_date": invoice_data["invoice"]["service_period"]["payment_due_date"],
                        "verbose": self.verbose
                    }
                    if not await operator.execute_operation(fill_invoice_issuance_data_form, step3_args, verbose=self.verbose):
                        raise Exception("Issuance data form filling failed")

                    # Step 4: Fill recipient form
                    step4_args = {
                        "issuer_type": invoice_data["issuer"]["type"],
                        "recipient_iva_condition": invoice_data["recipient"]["iva_condition"],
                        "recipient_cuit": invoice_data["recipient"]["cuit"],
                        "payment_method": invoice_data["invoice"]["payment"]["method"],
                        "verbose": self.verbose
                    }
                    if not await operator.execute_operation(fill_recipient_form, step4_args, verbose=self.verbose):
                        raise Exception("Recipient form filling failed")

                    # Step 5: Fill invoice content
                    step5_args = {
                        "issuer_type": invoice_data["issuer"]["type"],
                        "service_code": invoice_data["invoice"]["items"]["code"],
                        "service_concept": invoice_data["invoice"]["items"]["concept"],
                        "unit_price": str(invoice_data["invoice"]["items"]["unit_price"]),
                        "iva_rate": str(invoice_data["invoice"]["items"]["iva_rate"]),
                        "discount_percentage": str(invoice_data["invoice"]["items"]["discount_percentage"]),
                        "verbose": self.verbose
                    }
                    if not await operator.execute_operation(fill_invoice_content_form, step5_args, verbose=self.verbose):
                        raise Exception("Invoice content form filling failed")

                    result["status"] = "success"

            finally:
                await setup.close()

        except Exception as e:
            result["error"] = str(e)

        return result

    async def process_batch(self, batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process a batch of invoices concurrently.

        Args:
            batch: List of invoice data dictionaries

        Returns:
            List of processing results
        """
        tasks = [self.process_single_invoice(invoice) for invoice in batch]
        return await asyncio.gather(*tasks)

    async def process_all(self, invoices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process all invoices in batches.

        Args:
            invoices: List of all invoice data dictionaries

        Returns:
            List of all processing results
        """
        all_results = []
        for i in range(0, len(invoices), self.max_concurrent):
            batch = invoices[i:i + self.max_concurrent]
            if self.verbose:
                print(f"\nProcessing batch {i//self.max_concurrent + 1} ({len(batch)} invoices)")

            batch_results = await self.process_batch(batch)
            all_results.extend(batch_results)

            # Add delay between batches to avoid overwhelming the server
            if i + self.max_concurrent < len(invoices):
                await asyncio.sleep(self.delay_between_batches)

        return all_results
