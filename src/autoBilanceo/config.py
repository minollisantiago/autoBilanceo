from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent

# Data paths
DATA_DIR = BASE_DIR / "data"
TEMPLATE_PATH = DATA_DIR / "invoice_testing_template.json"
INVOICE_DATA_PATH = DATA_DIR / "invoice_data.json"
DOWNLOADS_PATH = DATA_DIR / "comprobantes"

# Prod Configuration
HEADLESS = True
VERBOSE = False
MAX_CONCURRENT = 4
DELAY_BETWEEN_BATCHES = 2

# Test Configuration
TEST_HEADLESS = False
TEST_VERBOSE = True
TEST_MAX_CONCURRENT = 4
TEST_DELAY_BETWEEN_BATCHES = 2