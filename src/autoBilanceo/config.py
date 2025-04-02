from pathlib import Path
from importlib import resources

def get_package_data_path(resource_path: str) -> Path:
    """Get the absolute path to a resource within the package's data directory."""
    with resources.path('autoBilanceo.data', resource_path) as path:
        return path

# Base paths - using package resources
DATA_DIR = resources.files('autoBilanceo') / 'data'

# Data paths
TEMPLATE_PATH = get_package_data_path('invoice_testing_template.json')
INVOICE_DATA_PATH = get_package_data_path('invoice_data.json')
DOWNLOADS_PATH = get_package_data_path('comprobantes')

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
