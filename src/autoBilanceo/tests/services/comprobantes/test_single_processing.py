import asyncio
from ....lib.services.comprobantes import InvoiceInputHandler, InvoiceBatchProcessor
from ....config import TEMPLATE_PATH, DOWNLOADS_PATH, TEST_HEADLESS, TEST_VERBOSE
# Warning filters are automatically applied when importing config

async def main():
    try:

        # Load invoice data
        input_handler = InvoiceInputHandler(TEMPLATE_PATH)

        # Initialize batch processor
        processor = InvoiceBatchProcessor(
            headless=TEST_HEADLESS, downloads_path=DOWNLOADS_PATH, verbose=TEST_VERBOSE
        )

        # Process single invoice (first one)
        # Set generate_invoice to False to avoid actually generating the invoice
        result = await processor.process_single_invoice(
            input_handler.get_invoice_data(0), generate_invoice=False
        )

        # Print results
        print("\nProcessing Results:")
        status = "✓" if result["status"] == "success" else "⨯"
        print(f"{status} Invoice for {result['issuer_cuit']} ({result['invoice_type']})")
        if result["error"]:
            print(f"   Error: {result['error']}")

    except Exception as e:
        print(f"Single invoice processing failed: {str(e)}")

def run():
    asyncio.run(main())

if __name__ == "__main__":
    run()
