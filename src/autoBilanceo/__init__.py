import asyncio
import argparse
from .lib.services.comprobantes import InvoiceInputHandler, InvoiceBatchProcessor
from .config import (
    TEMPLATE_PATH,
    DOWNLOADS_PATH,
    HEADLESS,
    VERBOSE,
    MAX_CONCURRENT,
    DELAY_BETWEEN_BATCHES,
)

def parse_args():
    parser = argparse.ArgumentParser(description='AutoBilanceo invoice processing')

    parser.add_argument(
        '--no-headless',
        action='store_false',
        dest='headless',
        default=HEADLESS,
        help=f'Run browser in visible mode (default: {HEADLESS})',
    )
    parser.add_argument(
        '--quiet',
        action='store_false',
        dest='verbose',
        default=VERBOSE,
        help=f'Reduce output verbosity (default: {VERBOSE})'
    )
    parser.add_argument(
        '--max-concurrent',
        type=int,
        default=MAX_CONCURRENT,
        help=f'Maximum concurrent processes (default: {MAX_CONCURRENT})'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=DELAY_BETWEEN_BATCHES,
        help=f'Delay between batches in seconds (default: {DELAY_BETWEEN_BATCHES})'
    )

    return parser.parse_args()

async def main():
    try:
        # Parse command line arguments
        args = parse_args()

        # Load invoice data
        input_handler = InvoiceInputHandler(TEMPLATE_PATH)

        # Initialize batch processor with CLI args or defaults
        processor = InvoiceBatchProcessor(
            max_concurrent=args.max_concurrent,
            delay_between_batches=args.delay,
            headless=args.headless,
            downloads_path=DOWNLOADS_PATH,
            verbose=args.verbose
        )

        # Process all invoices
        # Set generate_invoices to False to avoid actually generating the invoices
        results = await processor.process_all(
            input_handler.invoice_data, generate_invoices=True
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
