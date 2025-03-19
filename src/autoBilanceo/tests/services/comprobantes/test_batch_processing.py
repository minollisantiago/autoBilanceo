import asyncio
from pathlib import Path
from ....lib.services.comprobantes import InvoiceInputHandler, InvoiceBatchProcessor

async def main():
    try:
        # Load invoice data
        template_path = Path(__file__).parent.parent.parent.parent / "data" / "invoice_testing_template.json"
        input_handler = InvoiceInputHandler(template_path)

        # Initialize batch processor
        processor = InvoiceBatchProcessor(max_concurrent=2, delay_between_batches=2, headless=False, verbose=True)

        # Process all invoices
        results = await processor.process_all(input_handler.invoice_data)

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
