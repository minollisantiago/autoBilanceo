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

#### 2. Service Navigation Module
We've implemented secure navigation to AFIP services with:
- Service discovery and verification
- New window/tab handling
- Page state verification
- CUIT re-verification at service entry

#### 3. Invoice Generation Module
We've implemented the initial steps of invoice generation with:
- Empresa selection handling
- Navigation to invoice generator
- Punto de venta and invoice type selection with validation
- Human-like interaction patterns

### Overview of the application flow - browser automation
- ✓ Navigate to [Afip auth web](https://auth.afip.gob.ar/contribuyente_/login.xhtml)
- ✓ Authenticate
- ✓ Navigate to [Mis servicios](https://portalcf.cloud.afip.gob.ar/portal/app/mis-servicios)
- ✓ Find the `Comprobantes en línea` service
- ✓ Navigate to invoice generator
- ✓ Select punto de venta and invoice type
- [ ] Complete invoice form with data
- [ ] Submit form and verify success
- [ ] Implement batch processing
- [ ] Add CSV/Google Sheets integration

### Architecture

#### 1. Core Classes
- **AFIPAuthenticator**: Handles authentication and anti-detection
- **AFIPNavigator**: Manages service discovery and navigation
- **AFIPOperator**: New generic class for service-specific operations

#### 2. Service-Specific Modules
Located in `lib/services/`:
- **comprobantes.py**: Handles Comprobantes en línea service operations
  - `verify_rcel_page()`: Verifies service page state
  - `navigate_to_invoice_generator()`: Handles navigation to invoice generator
  - `select_invoice_type()`: Manages punto de venta and invoice type selection

#### 3. Models
Located in `models/`:
- **invoice_types.py**: Contains all invoice-related models and validation
  - `IssuerType`: Enum for issuer categories
  - `InvoiceType`: Enum for all available invoice types
  - `PuntoVenta`: Model for punto de venta validation
  - Validation functions for invoice type compatibility

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

3. **Currency Validation**
   - Validates against AFIP's official currency codes
   - Organized by geographical regions
   - Supports all AFIP-recognized currencies

4. **Issuance Data Validation**
   - Date format validation (dd/mm/yyyy)
   - Concept type validation (Products, Services, Both)
   - Billing period validation for services
   - Business rules enforcement:
     - Dates must be after year 2000
     - End date must be after start date
     - Payment due date must be after end date
     - Payment due date cannot be before today
     - Start date cannot be after today
     - Billing period required for services

5. **Payment Methods Validation**
   - Validates payment method selections for invoices
   - Supports multiple payment method selection
   - Validates card payment requirements
   - Ensures at least one payment method is selected
   - Maps to AFIP's official payment method codes

6. **IVA Condition Validation**
   - Validates recipient's IVA condition
   - Maps to AFIP's official condition codes
   - Ensures valid condition selection
   - Maintains Spanish descriptions for UI consistency

#### Code Examples

```python
# 1. Punto de Venta Validation Example
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

# 2. Currency Validation Example
from enum import StrEnum

class CurrencyCode(StrEnum):
    """Example of currency validation"""
    # European Currencies
    EURO = "060"
    LIBRA_ESTERLINA = "021"
    
    # North American Currencies
    DOLAR_ESTADOUNIDENSE = "DOL"
    DOLAR_CANADIENSE = "018"
    
    # South American Currencies
    PESO_CHILENO = "033"
    REAL_BRASILENO = "012"

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

    # Currency validation
    try:
        currency = CurrencyCode.DOLAR_ESTADOUNIDENSE  # Valid currency
        print(f"Valid currency code: {currency}")
    except ValueError as e:
        print(f"Invalid currency: {e}")

# 3. Issuance Data Validation Example
class ConceptType(IntEnum):
    """Concept types for invoices"""
    PRODUCTOS = 1
    SERVICIOS = 2
    PRODUCTOS_Y_SERVICIOS = 3

class IssuanceDate(BaseModel):
    """Date validation for AFIP format"""
    date: datetime

    @field_validator('date')
    @classmethod
    def validate_date_format(cls, v: datetime) -> datetime:
        if v < datetime(2000, 1, 1):
            raise ValueError('Date must be after year 2000')
        return v

    def format_for_afip(self) -> str:
        return self.date.strftime("%d/%m/%Y")

# Usage Examples
def example_issuance_validations():
    try:
        # Valid dates
        issuance_date = IssuanceDate.from_string("11/03/2024")
        
        # Valid concept type
        concept = ConceptType.SERVICIOS
        
        # Create billing period
        billing_period = BillingPeriod(
            start_date=IssuanceDate.from_string("01/03/2024"),
            end_date=IssuanceDate.from_string("31/03/2024"),
            payment_due_date=IssuanceDate.from_string("15/04/2024")
        )
        
        # These will raise validation errors:
        invalid_date = IssuanceDate.from_string("32/13/2024")  # Invalid date
        past_due = IssuanceDate.from_string("01/01/1999")      # Before 2000
        
    except ValueError as e:
        print(f"Validation error: {e}")

# 4. Payment Methods Validation Example
from enum import IntEnum
from typing import Set
from pydantic import BaseModel, Field

class PaymentMethod(IntEnum):
    """Payment methods available in AFIP's system"""
    CONTADO = 1
    TARJETA_DEBITO = 69
    TARJETA_CREDITO = 68
    CUENTA_CORRIENTE = 96
    CHEQUE = 97
    TRANSFERENCIA_BANCARIA = 91
    OTRA = 99
    OTROS_MEDIOS_ELECTRONICOS = 90

class PaymentMethodInfo(BaseModel):
    """Payment methods selection validation"""
    selected_methods: Set[PaymentMethod] = Field(
        default_factory=set,
        description="Set of selected payment methods"
    )

    @property
    def requires_card_data(self) -> bool:
        """Check if card data is required"""
        card_methods = {PaymentMethod.TARJETA_DEBITO, PaymentMethod.TARJETA_CREDITO}
        return any(method in card_methods for method in self.selected_methods)

# Usage Examples
def example_payment_validations():
    try:
        # Valid payment combination
        payment_info = create_payment_method_info(
            PaymentMethod.CONTADO,
            PaymentMethod.TARJETA_CREDITO
        )
        
        # Check if card data needed
        if payment_info.requires_card_data:
            print("Card data required")
        
        # This will raise an error:
        invalid_payment = create_payment_method_info()  # No methods selected
        
    except ValueError as e:
        print(f"Validation error: {e}")

# 5. IVA Condition Validation Example
from enum import IntEnum
from pydantic import BaseModel, Field

class IVACondition(IntEnum):
    """IVA conditions in AFIP's system"""
    IVA_RESPONSABLE_INSCRIPTO = 1
    RESPONSABLE_MONOTRIBUTO = 6
    MONOTRIBUTISTA_SOCIAL = 13
    MONOTRIBUTISTA_TRABAJADOR_INDEPENDIENTE_PROMOVIDO = 16

class IVAConditionInfo(BaseModel):
    """IVA condition validation"""
    condition: IVACondition = Field(
        description="IVA condition of the invoice recipient"
    )

# Mapping of descriptions
IVA_CONDITION_DESCRIPTIONS = {
    IVACondition.IVA_RESPONSABLE_INSCRIPTO: "IVA Responsable Inscripto",
    IVACondition.RESPONSABLE_MONOTRIBUTO: "Responsable Monotributo",
    IVACondition.MONOTRIBUTISTA_SOCIAL: "Monotributista Social",
    IVACondition.MONOTRIBUTISTA_TRABAJADOR_INDEPENDIENTE_PROMOVIDO: 
        "Monotributista Trabajador Independiente Promovido"
}

# Usage Examples
def example_iva_validations():
    try:
        # Valid IVA condition
        iva_info = create_iva_condition_info(
            IVACondition.IVA_RESPONSABLE_INSCRIPTO
        )
        print(f"IVA Condition: {IVA_CONDITION_DESCRIPTIONS[iva_info.condition]}")
        
    except ValueError as e:
        print(f"Validation error: {e}")

#### Environment Variables
The following environment variables are validated against these models:
```env
PUNTO_VENTA = 00005
ISSUER_TYPE = RESPONSABLE_INSCRIPTO
INVOICE_TYPE = FACTURA_A
CURRENCY = DOL  # USD Dollar code
CONCEPT_TYPE = SERVICIOS
PAYMENT_METHODS = ["CONTADO", "TARJETA_CREDITO"]  # Multiple methods allowed
IVA_CONDITION = "IVA_RESPONSABLE_INSCRIPTO"  # Recipient's IVA condition
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

4. **Currency**:
   - Must be a valid AFIP currency code
   - Codes vary in format (e.g., "DOL", "060", "021")
   - Grouped by geographical regions
   - Common codes:
     - "DOL": US Dollar
     - "060": Euro
     - "021": British Pound
     - "012": Brazilian Real

5. **Issuance Data**:
   - **Dates**:
     - Format: dd/mm/yyyy
     - Must be after year 2000
     - Logical sequence for billing period
   - **Concept Types**:
     - PRODUCTOS (1)
     - SERVICIOS (2)
     - PRODUCTOS_Y_SERVICIOS (3)
   - **Billing Period**:
     - Required for services
     - Start date ≤ End date
     - Payment due date ≥ End date
     - All dates validated against current date

6. **Payment Methods**:
   - At least one payment method must be selected
   - Multiple payment methods allowed
   - Card payments (credit/debit) require additional data
   - Valid codes:
     - "1": Contado
     - "69": Tarjeta de Débito
     - "68": Tarjeta de Crédito
     - "96": Cuenta Corriente
     - "97": Cheque
     - "91": Transferencia Bancaria
     - "99": Otra
     - "90": Otros medios electrónicos

7. **IVA Condition**:
   - Must be a valid AFIP condition code
   - Valid codes:
     - "1": IVA Responsable Inscripto
     - "6": Responsable Monotributo
     - "13": Monotributista Social
     - "16": Monotributista Trabajador Independiente Promovido
   - No default value - must be explicitly set
   - Spanish descriptions maintained for UI consistency

#### Error Handling
The validation system provides clear error messages for:
- Invalid punto de venta format
- Incompatible invoice type for issuer
- Invalid character types
- Length violations
- Invalid date formats
- Invalid date ranges
- Missing billing period for services
- Future start dates
- Past due dates
- Missing payment method selection
- Invalid payment method combinations
- Missing required card data
- Invalid IVA condition codes
- Missing IVA condition selection

### Testing
Test scripts are organized by service and functionality:

1. `test_auth`: Tests authentication only
```bash
uv run test_auth
```

2. `test_service_comprobantes`: Tests Comprobantes en línea service navigation
```bash
uv run test_service_comprobantes
```

3. `test_select_invoice_type`: Tests invoice type selection process
```bash
uv run test_select_invoice_type
```

### Next Steps in Development
- [ ] Complete invoice form automation
- [ ] Add form data validation models
- [ ] Implement form field mapping
- [ ] Add CSV/Google Sheets integration
- [ ] Implement concurrent processing
- [ ] Add proper logging system
- [ ] Implement error recovery mechanisms

### Development Guidelines
1. Always maintain human-like interaction patterns
2. Verify CUIT at critical steps
3. Use verbose logging during development
4. Keep service-specific code in dedicated modules
5. Follow the existing modular architecture
6. Implement proper validation for all input parameters
7. Use Pydantic models for data validation
8. Handle new window/tab contexts properly


