import asyncio
from .lib import RichArgumentParser
from .lib.services.comprobantes import InvoiceInputHandler, InvoiceBatchProcessor
from .config import (
    INVOICE_DATA_PATH,
    DOWNLOADS_PATH,
    HEADLESS,
    VERBOSE,
    MAX_CONCURRENT,
    DELAY_BETWEEN_BATCHES,
)
# Warning filters are automatically applied when importing config

#TODO: Added ventana_confirmacion.html element to inspect and verify the confirmation of the invoice generation, to avoid issues with false negatives if we cant generate the pdf due to a timeout

#TODO: Add retring loops, for when the page is slow and some invoices fail to generate
#TODO: Add an "issued" flag on input INVOICE_DATA_PATH json file so that we can rerun with the same json and ignore already issued invoices
#TODO: Ive noticed that we may encounter an issue where the invoice IS GENERATED but the process throws an error because either due to a timeout or 
#TODO: something else, we fail to download the pdf and store it on the data/ folder. Here is the error message we get:
#📄 Downloading invoice PDF...
#⨯ Failed to confirm invoice generation for CUIT 20326832392: Timeout 30000ms exceeded while waiting for event "download"
#=========================== logs ===========================
#waiting for event "download"
#============================================================

def parse_args():
    parser = RichArgumentParser(description='''[bold cyan]
 █████╗ ██╗   ██╗████████╗ ██████╗ ██████╗ ██╗██╗      █████╗ ███╗   ██╗ ██████╗███████╗ ██████╗
██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗██╔══██╗██║██║     ██╔══██╗████╗  ██║██╔════╝██╔════╝██╔═══██╗
███████║██║   ██║   ██║   ██║   ██║██████╔╝██║██║     ███████║██╔██╗ ██║██║     █████╗  ██║   ██║
██╔══██║██║   ██║   ██║   ██║   ██║██╔══██╗██║██║     ██╔══██║██║╚██╗██║██║     ██╔══╝  ██║   ██║
██║  ██║╚██████╔╝   ██║   ╚██████╔╝██████╔╝██║███████╗██║  ██║██║ ╚████║╚██████╗███████╗╚██████╔╝
╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═════╝ ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝╚══════╝ ╚═════╝[/bold cyan]

[bold blue]🚀 AFIP CLI tooling for dummies[/bold blue]
[bold green]🔗 Project repo: https://github.com/minollisantiago/autoBilanceo[/bold green]''')

    parser.add_argument(
        '--no-headless',
        action='store_false',
        dest='headless',
        default=HEADLESS,
        help='🖥️  Run browser in visible mode',
    )
    parser.add_argument(
        '--quiet',
        action='store_false',
        dest='verbose',
        default=VERBOSE,
        help='🔇 Reduce output verbosity'
    )
    parser.add_argument(
        '--max-concurrent',
        type=int,
        default=MAX_CONCURRENT,
        help='⚡ Maximum concurrent processes'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=DELAY_BETWEEN_BATCHES,
        help='⏱️  Delay between batches in seconds'
    )

    return parser.parse_args()

async def main():
    try:
        # Parse command line arguments
        args = parse_args()

        # Load invoice data
        input_handler = InvoiceInputHandler(INVOICE_DATA_PATH)

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
