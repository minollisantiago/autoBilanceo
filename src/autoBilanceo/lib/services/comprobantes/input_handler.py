import json
from pathlib import Path
from typing import List, Dict, Any

class InvoiceInputHandler:
    def __init__(self, invoice_json_path: str | Path | None = None):
        """
        Initialize the input handler with an optional invoice JSON file path.
        If no path is provided, it can be set later using load_invoice_file().
        """
        self.invoice_data: List[Dict[str, Any]] = []
        if invoice_json_path:
            self.load_invoice_file(invoice_json_path)

    def load_invoice_file(self, json_path: str | Path) -> None:
        """
        Load invoice data from a JSON file.

        Args:
            json_path: Path to the JSON file containing invoice data

        Raises:
            FileNotFoundError: If the JSON file doesn't exist
            json.JSONDecodeError: If the JSON data is malformed
        """
        path = Path(json_path)
        if not path.exists():
            raise FileNotFoundError(f"JSON file not found: {json_path}")

        with open(path, 'r') as f:
            self.invoice_data = json.load(f)

    def get_invoice_count(self) -> int:
        """Return the number of invoices to be processed."""
        return len(self.invoice_data)

    def get_invoice_batch(self, batch_size: int = 5) -> List[List[Dict[str, Any]]]:
        """
        Split invoices into batches for concurrent processing.

        Args:
            batch_size: Number of invoices per batch

        Returns:
            List of invoice data batches
        """
        return [
            self.invoice_data[i:i + batch_size]
            for i in range(0, len(self.invoice_data), batch_size)
        ]

    def get_invoice_data(self, invoice_index: int) -> Dict[str, Any]:
        """
        Get raw invoice data for a specific invoice.

        Args:
            invoice_index: Index of the invoice in the data list

        Returns:
            Dict containing all invoice data
        """
        return self.invoice_data[invoice_index]
