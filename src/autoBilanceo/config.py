import warnings
from pathlib import Path

# Warning Configuration
# -----------------------------------------------------------------------------
# Known Issue: During test execution, particularly on Windows systems, asyncio 
# subprocess handling generates ResourceWarnings and exceptions related to pipe 
# cleanup. These warnings appear as:
#   1. "Exception ignored in: <function BaseSubprocessTransport.__del__ at 0x...>"
#   2. "ValueError: I/O operation on closed pipe"
#   3. "ResourceWarning: unclosed transport"
#
# Root Cause:
# - These warnings occur during asyncio's subprocess handling and pipe cleanup
# - They happen when Python tries to clean up pipes that are already functionally closed
# - Common in Windows systems due to how Windows handles process cleanup
#
# Impact:
# - These warnings are harmless and don't affect application functionality
# - The invoice generation process completes successfully
# - Resources are properly cleaned up by Python's garbage collector
#
# Solution:
# We suppress these specific warnings to reduce noise in test output while
# maintaining visibility of other important warnings and errors
#warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed transport")
#warnings.filterwarnings("ignore", message="Exception ignored.*BaseSubprocessTransport.*")

# Base paths
BASE_DIR = Path(__file__).parent

# Data paths
DATA_DIR = BASE_DIR / "data"
TEMPLATE_PATH = DATA_DIR / "invoice_testing_template.json"
INVOICE_DATA_PATH = DATA_DIR / "invoice_data.json"
DOWNLOADS_PATH = DATA_DIR / "comprobantes"

# Prod Configuration
HEADLESS = True
VERBOSE = True
MAX_CONCURRENT = 4
DELAY_BETWEEN_BATCHES = 2

# Test Configuration
TEST_HEADLESS = False
TEST_VERBOSE = True
TEST_MAX_CONCURRENT = 4
TEST_DELAY_BETWEEN_BATCHES = 2
