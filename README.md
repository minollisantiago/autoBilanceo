### General
- This project's objective is to develop a set of browser automation tooling
- Its end user is non technical users, but the tools should be usable via CLI commands using the uv package manager as well as via python scripts, to be excecuted using uv as well (uv run ...)
- The main() script should be on src/autoBilanceo/__init__.py

### Implementation Progress

#### 1. Authentication Module
We've implemented secure browser automation for AFIP authentication with the following features:
- Anti-detection measures
- Human-like interaction patterns
- Geolocation spoofing (Córdoba, Argentina)
- Secure credential management via environment variables

##### System Requirements
Before running the automation, ensure you have the necessary dependencies:
```bash
# Install system dependencies
sudo apt-get install libnss3 libnspr4 libasound2t64

# Install browser binaries
uv run playwright install
```

##### Environment Setup
Create a `.env` file in your project root:

### Overview of the application flow - browser automation
- Navigate to [Afip auth web](https://auth.afip.gob.ar/contribuyente_/login.xhtml)
- Authenticate
- Navigate to [Mis servicios](https://portalcf.cloud.afip.gob.ar/portal/app/mis-servicios)
- Find the `Comprobantes en línea` service
- Complete a form with invoice data and then send the form (POST request)
- This process will be repeated n times (less than 200 times) asynchronously
- The data needed to fill the invoice form each time will be either on a csv file or a google sheet in the form of an n * m matrix where n is going to be each invoice issuer and m is going to be the different fields needed to complete the invoice form, the auth data will be included on those m columns

##### Testing
Two main test scripts are provided:
1. `test_auth`: Tests authentication only
```bash
uv run test_auth
```

2. `test_auth_plus_navigation`: Tests full navigation flow
```bash
uv run test_service_comprobantes
```

#### Security Features

1. **Browser Anti-Detection**:
   - Custom user agent rotation
   - Viewport randomization
   - Geolocation spoofing (Córdoba)
   - Timezone and locale configuration
   - Disabled automation flags

2. **Human-like Interaction**:
   ```python
   await asyncio.sleep(random.uniform(0.5, 1))  # Random delays
   await element.type(char, delay=random.uniform(100, 300))  # Natural typing
   ```

3. **Verification Systems**:
   - CUIT verification at login
   - CUIT re-verification at service entry
   - Page structure verification
   - Service-specific element checks

#### Next Steps in Development
- [ ] Implement invoice form automation
- [ ] Add CSV/Google Sheets integration
- [ ] Implement concurrent processing
- [ ] Add proper logging system
- [ ] Implement error recovery mechanisms

### Overview of the application flow - browser automation
- ✓ Navigate to [Afip auth web](https://auth.afip.gob.ar/contribuyente_/login.xhtml)
- ✓ Authenticate
- ✓ Navigate to [Mis servicios](https://portalcf.cloud.afip.gob.ar/portal/app/mis-servicios)
- ✓ Find the `Comprobantes en línea` service
- [ ] Complete a form with invoice data and then send the form (POST request)
- [ ] This process will be repeated n times (less than 200 times) asynchronously
- [ ] The data needed to fill the invoice form each time will be either on a csv file or a google sheet

### Error Handling
The system includes comprehensive error handling:
- Authentication failures
- Navigation timeouts
- CUIT mismatches
- Service availability issues
- Page structure changes

### Development Guidelines
1. Always maintain human-like interaction patterns
2. Verify CUIT at critical steps
3. Use verbose logging during development
4. Keep service-specific code in dedicated modules
5. Follow the existing modular architecture

### Input Validation

#### Invoice Parameters Validation
The system implements strict validation for various invoice parameters using Pydantic v2. Here are the key validations:

1. **Punto de Venta Validation**
   - Must be exactly 5 digits
   - Only numeric characters allowed
   - Automatically pads with leading zeros

2. **Invoice Type Validation**
   - Validates against allowed types per issuer category
   - Ensures compatibility between issuer type and invoice type

#### Code Examples

```python
from pydantic import BaseModel, Field, field_validator
from enum import IntEnum, auto
from typing import Optional

# Issuer Types
class IssuerType(IntEnum):
    RESPONSABLE_INSCRIPTO = auto()
    MONOTRIBUTO = auto()

# Punto de Venta Validation
class PuntoVenta(BaseModel):
    """
    Model for validating Punto de Venta number
    Must be exactly 5 digits, numbers only
    """
    number: str = Field(..., min_length=5, max_length=5)

    @field_validator('number')
    @classmethod
    def validate_punto_venta(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError('Punto de venta must contain only numbers')
        if len(v) != 5:
            raise ValueError('Punto de venta must be exactly 5 digits long')
        return v

    @classmethod
    def from_string(cls, value: str) -> 'PuntoVenta':
        # Pad with leading zeros if necessary
        padded_value = value.zfill(5)
        return cls(number=padded_value)

# Usage Examples
def example_validations():
    # Valid punto de venta
    valid_pv = PuntoVenta.from_string("00005")  # Works fine
    
    # These will raise validation errors:
    try:
        PuntoVenta(number="123")     # Too short
    except ValueError as e:
        print(f"Validation error: {e}")
    
    try:
        PuntoVenta(number="12A45")   # Contains a letter
    except ValueError as e:
        print(f"Validation error: {e}")
```

#### Environment Variables
The following environment variables are validated against these models:
```env
PUNTO_VENTA = 00005
ISSUER_TYPE = RESPONSABLE_INSCRIPTO
INVOICE_TYPE = FACTURA_A
```

#### Validation Rules Summary
1. **Punto de Venta**:
   - Format: 5 digits (e.g., "00005")
   - Auto-padding: "5" → "00005"
   - Invalid: "123" (too short), "12A45" (non-numeric)

2. **Issuer Type**:
   - Valid values: RESPONSABLE_INSCRIPTO, MONOTRIBUTO
   - Determines allowed invoice types

3. **Invoice Type**:
   - Must match issuer type (e.g., FACTURA_A only for RESPONSABLE_INSCRIPTO)
   - Validated against AFIP's official invoice type codes

#### Error Handling
The validation system provides clear error messages:
- Invalid punto de venta format
- Incompatible invoice type for issuer
- Invalid character types
- Length violations


