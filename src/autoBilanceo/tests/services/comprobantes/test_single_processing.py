import asyncio
from pathlib import Path
from ....lib.services.comprobantes import InvoiceInputHandler, InvoiceBatchProcessor

async def main():
    try:

        # Data paths
        template_path = Path(__file__).parent.parent.parent.parent / "data" / "invoice_testing_template.json"
        downloads_path = Path(__file__).parent.parent.parent.parent / "data" / "comprobantes"

        # Load invoice data
        input_handler = InvoiceInputHandler(template_path)

        # Initialize batch processor
        processor = InvoiceBatchProcessor(
            headless=False, downloads_path=downloads_path, verbose=True
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
