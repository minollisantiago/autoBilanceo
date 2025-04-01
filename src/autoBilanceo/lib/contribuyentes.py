import json
import argparse
from typing import Dict
from pathlib import Path

from ..models.cuit import create_cuit_number
from .argparser import RichArgumentParser

def load_contribuyentes(file_path: Path) -> Dict[str, str]:
    """Load contribuyentes from JSON file"""
    if not file_path.exists():
        return {}
    with open(file_path, 'r') as f:
        return json.load(f)

def save_contribuyentes(file_path: Path, data: Dict[str, str]) -> None:
    """Save contribuyentes to JSON file"""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def add_contribuyente(cuit: str, password: str, file_path: Path) -> bool:
    """Add a new contribuyente to the JSON file"""
    try:
        # Validate CUIT using existing model
        validated_cuit = create_cuit_number(cuit)

        # Load existing data
        contribuyentes = load_contribuyentes(file_path)

        # Add new entry
        contribuyentes[validated_cuit.number] = password

        # Save back to file
        save_contribuyentes(file_path, contribuyentes)
        return True
    except ValueError as e:
        print(f"Error: Invalid CUIT format - {e}")
        return False
    except Exception as e:
        print(f"Error: Failed to add contribuyente - {e}")
        return False

def main():
    parser = RichArgumentParser(description='''[bold blue]🔑 AFIP Contribuyente Management Tool[/bold blue]
[bold green]🔗 Project repo: https://github.com/minollisantiago/autoBilanceo[/bold green]''')

    parser.add_argument(
        '--cuit',
        required=True,
        help='🔢 CUIT number of the contribuyente (11 digits)'
    )
    parser.add_argument(
        '--password',
        required=True,
        help='🔐 Password (clave fiscal) for the contribuyente'
    )

    args = parser.parse_args()

    # Get the contribuyentes.json path relative to this file
    file_path = Path(__file__).parent.parent / 'data' / 'contribuyentes.json'

    if add_contribuyente(args.cuit, args.password, file_path):
        print(f"✓ Successfully added contribuyente with CUIT: {args.cuit}")
    else:
        print("⨯ Failed to add contribuyente")

if __name__ == "__main__":
    main()
