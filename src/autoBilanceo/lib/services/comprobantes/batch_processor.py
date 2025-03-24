import asyncio
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Any, Optional
from .verify_rcel_page import verify_rcel_page
from .step1_nav_to_invoice_generator import navigate_to_invoice_generator
from .step2_select_invoice_type import select_invoice_type
from .step3_fill_invoice_issuance_data_form import fill_invoice_issuance_data_form
from .step4_fill_recipient_form import fill_recipient_form
from .step5_fill_invoice_content_form import fill_invoice_content_form
from .step6_generate_invoice import confirm_invoice_generation
from ....lib import BrowserSetup, AFIPAuthenticator, AFIPNavigator, AFIPOperator

class InvoiceBatchProcessor:
    def __init__(
        self,
        max_concurrent: int = 3,
        delay_between_batches: int = 2,
        headless: bool = True,
        downloads_path: Optional[Path] = None,
        verbose: bool = False
    ):
        """
        Initialize the batch processor.

        Args:
            max_concurrent (int): Maximum number of concurrent browser instances.
            delay_between_batches (int): Seconds to wait between batch processing.
            headless (bool): Whether to run browsers in headless mode.
            downloads_path (Optional[Path]): Custom path for storing downloaded PDFs.
                If provided, PDFs will be organized in CUIT-specific folders.
                If None, files will be stored in Playwright's temporary directory.
            verbose (bool): Whether to print progress messages.

        Note:
            When downloads_path is not provided, invoice PDFs are stored in
            Playwright's temporary directory and are automatically cleaned up
            when the browser session ends.
        """
        self.max_concurrent = max_concurrent
        self.delay_between_batches = delay_between_batches
        self.headless = headless
        self.downloads_path = downloads_path
        self.verbose = verbose
        self.results: List[Dict[str, Any]] = []

    def _create_issuer_groups(self, invoices: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group invoices by issuer CUIT.

        Args:
            invoices: List of invoice data dictionaries

        Returns:
            Dictionary with CUIT as key and list of invoices as value
        """
        groups = defaultdict(list)
        for invoice in invoices:
            issuer_cuit = invoice["issuer"]["cuit"]
            groups[issuer_cuit].append(invoice)
        return dict(groups)

    def _create_batches(self, invoices: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """
        Create batches ensuring no batch contains multiple invoices from the same issuer.

        Args:
            invoices: List of invoice data dictionaries

        Returns:
            List of batches (each batch is a list of invoices)
        """
        # Group invoices by issuer
        issuer_groups = self._create_issuer_groups(invoices)

        # Initialize batches
        batches = []
        current_batch = []
        used_issuers = set()

        # Keep track of remaining invoices per issuer
        remaining_invoices = {
            cuit: list(invoices) 
            for cuit, invoices in issuer_groups.items()
        }

        while any(remaining_invoices.values()):  # While there are invoices to process
            current_batch = []
            used_issuers = set()

            # Try to add one invoice from each issuer until batch is full
            for cuit, invoices in list(remaining_invoices.items()):
                # Skip if we've already used this issuer in this batch or if the batch is full
                if cuit in used_issuers or len(current_batch) >= self.max_concurrent:
                    continue

                # If this issuer still has invoices
                if invoices:
                    invoice = invoices.pop(0)       #Get first invoice from invoices and remove it
                    current_batch.append(invoice)   # Add the invoice to the current_batch
                    used_issuers.add(cuit)          #Mark the CUIT as used on the batch

                    # If no more invoices for this issuer, remove it from remaining
                    if not invoices:
                        del remaining_invoices[cuit]

            # Add the batch if it's not empty
            if current_batch:
                batches.append(current_batch)

        return batches

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
            "error": None,
        }

        try:
            # Setup browser
            setup = BrowserSetup(headless=self.headless, downloads_path=self.downloads_path)
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
                        "invoice_type": invoice_data["invoice"]["type"],
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

                    # Step 6: Generate invoice
                    step6_args = {
                        "issuer_cuit": invoice_data["issuer"]["cuit"],
                        "downloads_path": self.downloads_path,
                        "verbose": self.verbose
                    }
                    if not await operator.execute_operation(confirm_invoice_generation, step6_args, verbose=self.verbose):
                        raise Exception(f"Invoice generation failed")

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
        Process all invoices in batches, ensuring no concurrent processing of same issuer.

        Args:
            invoices: List of all invoice data dictionaries

        Returns:
            List of all processing results
        """
        all_results = []
        batches = self._create_batches(invoices)

        for i, batch in enumerate(batches):
            if self.verbose:
                issuers = {invoice["issuer"]["cuit"] for invoice in batch}
                print(f"\nProcessing batch {i + 1}/{len(batches)}")
                print(f"Batch size: {len(batch)} invoice(s)")
                print(f"Unique issuers in batch: {len(issuers)}. LIST OF CUITS: [{issuers}]")
                for invoice in batch:
                    print(f"  - CUIT: {invoice['issuer']['cuit']}, "
                          f"Type: {invoice['invoice']['type']}")

            batch_results = await self.process_batch(batch)
            all_results.extend(batch_results)

            # Add delay between batches if not the last batch
            if i < len(batches) - 1:
                await asyncio.sleep(self.delay_between_batches)

        return all_results
