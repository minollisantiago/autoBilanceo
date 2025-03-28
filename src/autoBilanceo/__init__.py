import asyncio
import warnings
from .lib import RichArgumentParser
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
    """
    # Known Issue & Solution:
    # There's a harmless but noisy warning that occurs during invoice generation,
    # specifically on Windows systems. The error looks like:
    # "Exception ignored in: <function BaseSubprocessTransport.__del__ at 0x...>"
    # followed by "ValueError: I/O operation on closed pipe"
    #
    # This happens because:
    # 1. It's related to asyncio subprocess handling and pipe cleanup
    # 2. The pipe is already functionally closed when Python tries to clean it up
    # 3. The warning doesn't affect the actual invoice generation functionality
    #
    # We suppress this specific warning while keeping other important warnings visible.
    # If you need to track all warnings during development, consider making this
    # suppression conditional based on an environment variable.
    """
    warnings.filterwarnings(
        "ignore", category=ResourceWarning, message="unclosed transport"
    )

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
