import asyncio
from ....lib.services.comprobantes import InvoiceInputHandler, InvoiceBatchProcessor
from ....config import (
    TEMPLATE_PATH,
    DOWNLOADS_PATH,
    TEST_HEADLESS,
    TEST_VERBOSE,
    TEST_MAX_CONCURRENT,
    TEST_DELAY_BETWEEN_BATCHES
)

async def main():
    try:

        # Load invoice data
        input_handler = InvoiceInputHandler(TEMPLATE_PATH)

        # Initialize batch processor
        processor = InvoiceBatchProcessor(
            max_concurrent=TEST_MAX_CONCURRENT,
            delay_between_batches=TEST_DELAY_BETWEEN_BATCHES,
            headless=TEST_HEADLESS,
            downloads_path=DOWNLOADS_PATH,
            verbose=TEST_VERBOSE
        )

        # Process all invoices
        # Set generate_invoices to False to avoid actually generating the invoices
        results = await processor.process_all(
            input_handler.invoice_data, generate_invoices=False
        )

        # Print results
        print("\nProcessing Results:")
        for result in results:
            status = "✓" if result["status"] == "success" else "⨯"
            print(f"{status} Invoice for {result['issuer_cuit']} ({result['invoice_type']})")
            if result["error"]:
                print(f"   Error: {result['error']}")

    except Exception as e:
        print(f"Batch processing failed: {str(e)}")

def run():
    asyncio.run(main())

if __name__ == "__main__":
    run()
