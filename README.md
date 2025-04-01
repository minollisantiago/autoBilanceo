### General
- This project's objective is to develop a set of browser automation tooling for [afips website](https://auth.afip.gob.ar/contribuyente_/login.xhtml).
- Its end user is non technical users, but the tools should be usable via CLI commands using the uv package manager as well as via python scripts, to be excecuted using uv as well (uv run ...)
- The main() script should be on src/autoBilanceo/__init__.py

### Architecture

#### 1. Core Classes
- **BrowserSetup**: Core browser initialization and anti-detection
  - Advanced anti-detection measures:
    - User agent rotation (Chrome, Edge, Safari)
    - Viewport randomization
    - Geolocation spoofing (Córdoba, Argentina)
    - Browser fingerprint modification
    - Custom HTTP headers
  - Human-like interaction patterns:
    - Random timing delays
    - Natural typing simulation
    - Realistic mouse movements
  - Security features:
    - Disabled automation flags
    - Reduced fingerprinting surface
    - Secure context handling

- **AFIPAuthenticator**: Authentication management
  - Secure credential handling via environment variables
  - Multi-step authentication flow:
    - CUIT entry and validation
    - Password handling
    - Post-login verification
  - Human-like interaction patterns:
    - Natural typing delays
    - Random timing between actions
  - Robust error handling and validation:
    - CUIT verification after login
    - Connection state monitoring
    - Detailed error reporting

- **AFIPNavigator**: Service navigation (existing implementation)
  - Service discovery and verification
  - New window/tab handling
  - Page state verification
  - CUIT re-verification at service entry

- **AFIPOperator**: Service operations (existing implementation)
  - Generic class for service-specific operations
  - Standardized operation patterns
  - Error handling and recovery

#### 2. Service-Specific Modules
Located in `lib/services/comprobantes/`:
- **Invoice Generation Flow**: Sequential steps for automated invoice creation
  - `step1_nav_to_invoice_generator.py`: Initial navigation
    - Handles empresa selection
    - Navigates to invoice generator interface
    - Implements random delays for human-like interaction
  
  - `step2_select_invoice_type.py`: Invoice configuration
    - Validates and selects punto de venta from environment
    - Validates issuer type compatibility
    - Handles invoice type selection and validation
    - Ensures proper form state between selections
  
  - `step3_fill_invoice_issuance_data_form.py`: Issuance details
    - Validates and fills issuance date
    - Handles concept type selection (Products/Services/Both)
    - Manages billing period for services:
      - Start date validation
      - End date validation
      - Payment due date validation
    - Implements business rules for date ranges
  
  - `step4_fill_recipient_form.py`: Recipient information
    - Validates and fills IVA condition based on issuer type
    - Handles CUIT number validation and input
    - Manages payment method selection:
      - Supports multiple payment methods
      - Handles card payment requirements
      - Validates payment method combinations
  
  - `step5_fill_invoice_content_form.py`: Invoice details
    - Validates and fills service information:
      - Service code validation
      - Service concept description
      - Unit price handling
    - Manages optional discount percentages
    - Handles IVA rates for RESPONSABLE_INSCRIPTO:
      - Supports all valid AFIP rates (0%, 2.5%, 5%, 10.5%, 21%, 27%)
      - Handles special cases (NO_GRAVADO, EXENTO)
    - Implements proper form state management

  - `step6_generate_invoice.py`: Final invoice generation
    - Handles confirmation dialog automation
    - Manages AJAX-based invoice generation process
    - Implements response validation:
      - Success case: 
        - Captures generated invoice ID
        - Downloads invoice PDF
        - Organizes PDFs by CUIT in custom directory (optional)
      - Error cases:
        - PDF generation errors
        - Authorization code (CAE) errors
        - Additional data errors
    - Flexible PDF storage options:
      - Custom directory with CUIT-based organization
      - Temporary storage with automatic cleanup
    - Provides detailed operation status and error reporting

#### 3. Models
Located in `models/`:
- **invoice_types.py**: Core invoice type definitions
  - `IssuerType`: Enum for issuer categories (RESPONSABLE_INSCRIPTO, MONOTRIBUTO)
  - `InvoiceType`: Comprehensive enum for all AFIP invoice types (A, B, C, etc.)
  - `PuntoVenta`: Model for punto de venta validation with auto-padding
  - Validation functions for invoice type compatibility per issuer

- **invoice_currency.py**: Currency handling
  - `CurrencyCode`: Enum covering all AFIP-supported currencies
  - Organized by regions (Asian, European, American, etc.)
  - Includes special units (e.g., Derechos Especiales de Giro)
  - Full Spanish descriptions for UI display

- **invoice_issuance_data.py**: Issuance details validation
  - `ConceptType`: Enum for product/service types
  - `IssuanceDate`: Date validation with AFIP format handling
  - `BillingPeriod`: Period validation for service invoices
  - Business rules enforcement for date ranges

- **invoice_recipient_data.py**: Recipient information
  - `IVACondition`: Comprehensive IVA condition validation
  - `CUITNumber`: CUIT validation with format cleaning
  - Issuer-specific validation rules
  - Spanish descriptions for UI consistency

- **invoice_payment_methods.py**: Payment handling
  - `PaymentMethod`: Enum for all AFIP payment methods
  - Support for multiple payment method selection
  - Card payment requirement detection
  - Validation for payment method combinations

- **invoice_content_services.py**: Service invoice content
  - `IVARate`: VAT rate validation with AFIP internal codes
  - `ServiceCode`: Service code validation with auto-padding
  - `UnitPrice`: Price validation with decimal handling
  - `DiscountPercentage`: Discount validation with limits
  - Automatic calculations for:
    - Discounted prices
    - VAT amounts
    - Total prices
  - Different validation rules for:
    - RESPONSABLE_INSCRIPTO (requires VAT)
    - MONOTRIBUTO (no VAT handling)

### Implementation Progress

#### 1. Authentication Module
We've implemented secure browser automation for AFIP authentication with the following features:
- Advanced CUIT validation using Pydantic models
- Anti-detection measures
- Human-like interaction patterns
- Geolocation spoofing (Córdoba, Argentina)
- Secure credential management via environment variables

```python
# Authentication with CUIT Validation Example
from models.cuit import create_cuit_number
from lib.auth import AFIPAuthenticator

async def example_authentication():
    # Valid CUIT authentication
    try:
        auth = AFIPAuthenticator(page)
        success = await auth.authenticate(
            cuit="20-12345678-9",  # Will be automatically cleaned and validated
            verbose=True
        )
        if success:
            print("✓ Authentication successful")
    except ValueError as e:
        print(f"⨯ Authentication failed: {e}")

    # Invalid CUIT format
    try:
        await auth.authenticate(
            cuit="123",  # Too short, will fail validation
            verbose=True
        )
    except ValueError as e:
        print(f"⨯ Authentication failed: Invalid CUIT format")

    # CUIT verification after login
    try:
        success = await auth.verify_CUIT("20-12345678-9")
        if success:
            print("✓ CUIT verification successful")
    except ValueError as e:
        print(f"⨯ CUIT verification failed: {e}")
```

Key Features:
- Strict CUIT validation before authentication attempt
- Automatic cleaning of CUIT format (removes hyphens and spaces)
- Double validation during login verification
- Clear error messages for invalid formats
- Integration with Pydantic validation models

Error Handling:
- Invalid CUIT format (non-numeric characters)
- Incorrect CUIT length
- CUIT mismatch after login
- Missing or invalid credentials

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
- ✓ Complete invoice form with data
- ✓  Submit form and verify success
- [ ] Implement batch processing
- [ ] Add CSV/Google Sheets integration


### Input Validation
#### Invoice Parameters Validation

The system implements strict validation for various invoice parameters using Pydantic v2. Here are the key validations:

1.  **Punto de Venta Validation**

    *   Must be exactly 5 digits
    *   Only numeric characters allowed
    *   Automatically pads with leading zeros

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

2.  **Invoice Type Validation**

    *   Validates against allowed types per issuer category
    *   Ensures compatibility between issuer type and invoice type

3.  **Currency Validation**

    *   Validates against AFIP's official currency codes
    *   Organized by geographical regions
    *   Supports all AFIP-recognized currencies

    ```python
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
        # Currency validation
        try:
            currency = CurrencyCode.DOLAR_ESTADOUNIDENSE  # Valid currency
            print(f"Valid currency code: {currency}")
        except ValueError as e:
            print(f"Invalid currency: {e}")
    ```

4.  **Issuance Data Validation**

    *   Base date validation (AFIPDate) for all invoice dates:
        *   Format validation (dd/mm/yyyy)
        *   Must be after year 2000
    *   Specific issuance date validation with 10-day window rule
    *   Concept type validation (Products, Services, Both)
    *   Billing period validation for services

    ```python
    # 3. Issuance Data Validation Example
    from datetime import datetime, timedelta
    from pydantic import BaseModel, field_validator, model_validator

    class AFIPDate(BaseModel):
        """Base model for all AFIP dates"""
        date: datetime

        @field_validator('date')
        @classmethod
        def validate_date_format(cls, v: datetime) -> datetime:
            if v < datetime(2000, 1, 1):
                raise ValueError('Date must be after year 2000')
            return v

        @classmethod
        def from_string(cls, value: str) -> 'AFIPDate':
            try:
                parsed_date = datetime.strptime(value, "%d/%m/%Y")
                return cls(date=parsed_date)
            except ValueError as e:
                raise ValueError(f'Date: {value} must be in dd/mm/yyyy format')

    class IssuanceDate(BaseModel):
        """Model for invoice issuance date with specific rules"""
        issuance_date: AFIPDate

        @model_validator(mode='after')
        def validate_issuance_window(self) -> 'IssuanceDate':
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            ten_days_ago = today - timedelta(days=10)
            ten_days_ahead = today + timedelta(days=10)

            if self.issuance_date.date < ten_days_ago:
                raise ValueError('Issuance date cannot be more than 10 days in the past')
            if self.issuance_date.date > ten_days_ahead:
                raise ValueError('Issuance date cannot be more than 10 days in the future')
            return self

    class BillingPeriod(BaseModel):
        """Model for service billing periods"""
        start_date: AFIPDate
        end_date: AFIPDate
        payment_due_date: AFIPDate

        @model_validator(mode='after')
        def validate_date_ranges(self) -> 'BillingPeriod':
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            if self.end_date.date < self.start_date.date:
                raise ValueError('End date cannot be before start date')
            if self.payment_due_date.date < self.end_date.date:
                raise ValueError('Payment due date cannot be before end date')
            if self.payment_due_date.date < today:
                raise ValueError('Payment due date cannot be before today')
            if self.start_date.date > today:
                raise ValueError('Start date cannot be after today')
            return self

    # Usage Examples
    def example_date_validations():
        try:
            # Create an issuance date (5 days from now)
            future_date = (datetime.now() + timedelta(days=5)).strftime("%d/%m/%Y")
            issuance = IssuanceDate(
                issuance_date=AFIPDate.from_string(future_date)
            )
            print("Valid issuance date")

            # Create a billing period
            billing = BillingPeriod(
                start_date=AFIPDate.from_string("01/03/2024"),
                end_date=AFIPDate.from_string("31/03/2024"),
                payment_due_date=AFIPDate.from_string("15/04/2024")
            )
            print("Valid billing period")

        except ValueError as e:
            print(f"Validation error: {e}")

        # Error cases
        try:
            # Invalid: 15 days in the future
            invalid_date = (datetime.now() + timedelta(days=15)).strftime("%d/%m/%Y")
            IssuanceDate(
                issuance_date=AFIPDate.from_string(invalid_date)
            )
        except ValueError as e:
            print("Error: Issuance date cannot be more than 10 days in the future")
    ```

Key changes:
1. Separated base date validation (`AFIPDate`) from specific issuance rules (`IssuanceDate`)
2. Simplified validation chain using composition instead of inheritance
3. Clearer separation of concerns:
   - `AFIPDate`: Basic format and year 2000 validation
   - `IssuanceDate`: 10-day window rule
   - `BillingPeriod`: Date sequence validation

5.  **Payment Methods Validation**

    *   Validates payment method selections for invoices
    *   Supports multiple payment method selection
    *   Validates card payment requirements
    *   Ensures at least one payment method is selected
    *   Maps to AFIP's official payment method codes

    ```python
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
    ```

6.  **IVA Condition Validation**

    *   Validates recipient's IVA condition
    *   Maps to AFIP's official condition codes
    *   Ensures valid condition selection
    *   Maintains Spanish descriptions for UI consistency

    ```python
    # 5. IVA Condition Validation Example
    from enum import IntEnum
    from pydantic import BaseModel, Field, model_validator
    from .invoice_types import IssuerType

    class IVACondition(IntEnum):
        """IVA conditions in AFIP's system"""
        # Common conditions for both issuer types
        IVA_RESPONSABLE_INSCRIPTO = 1
        RESPONSABLE_MONOTRIBUTO = 6
        MONOTRIBUTISTA_SOCIAL = 13
        MONOTRIBUTISTA_TRABAJADOR_INDEPENDIENTE_PROMOVIDO = 16

        # Additional conditions for MONOTRIBUTO issuer
        IVA_SUJETO_EXENTO = 4
        CONSUMIDOR_FINAL = 5
        SUJETO_NO_CATEGORIZADO = 7
        PROVEEDOR_DEL_EXTERIOR = 8
        CLIENTE_DEL_EXTERIOR = 9
        IVA_LIBERADO_LEY_19640 = 10
        IVA_NO_ALCANZADO = 15

    class IVAConditionInfo(BaseModel):
        """IVA condition validation"""
        condition: IVACondition = Field(
            description="IVA condition of the invoice recipient"
        )
        issuer_type: IssuerType = Field(
            description="Type of issuer creating the invoice"
        )

        def validate_condition_for_issuer(self) -> bool:
            if self.issuer_type == IssuerType.RESPONSABLE_INSCRIPTO:
                valid_conditions = {IVACondition.IVA_RESPONSABLE_INSCRIPTO}
            else:  # MONOTRIBUTO
                valid_conditions = {IVACondition.IVA_RESPONSABLE_INSCRIPTO, IVACondition.CONSUMIDOR_FINAL}
                
            if self.condition not in valid_conditions:
                raise ValueError(f'Invalid IVA condition {self.condition} for issuer type {self.issuer_type}')
            return True

    # Usage Examples
    def example_iva_validations():
        try:
            # Valid combination: Monotributo issuer can have Consumidor Final condition
            valid_iva = IVAConditionInfo(
                condition=IVACondition.CONSUMIDOR_FINAL,
                issuer_type=IssuerType.MONOTRIBUTO
            )
            valid_iva.validate_condition_for_issuer()
            print("Success! Valid IVA condition for issuer type")
        except ValueError as e:
            print(f"Error: {e}")

        try:
            # Invalid combination: Responsable Inscripto cannot have Consumidor Final condition
            invalid_iva = IVAConditionInfo(
                condition=IVACondition.CONSUMIDOR_FINAL,
                issuer_type=IssuerType.RESPONSABLE_INSCRIPTO
            )
            invalid_iva.validate_condition_for_issuer()
            print("This line won't be reached")
        except ValueError as e:
            print(f"Error: {e}")  # Output: Error: Invalid IVA condition 5 for issuer type 1
    ```

7.  **CUIT Validation**

    *   Validates CUIT (Código Único de Identificación Tributaria)
    *   Ensures exactly 11 digits
    *   Validates numeric-only input
    *   Automatic cleaning of non-numeric characters
    *   Prepared for future taxpayer type and verification digit validations

    ```python
    # 6. CUIT Validation Example
    from pydantic import BaseModel, Field

    class CUITNumber(BaseModel):
        number: str = Field(..., min_length=11, max_length=11)
        
        @classmethod
        def from_string(cls, value: str) -> 'CUITNumber':
            # Remove any non-numeric characters
            cleaned_value = ''.join(filter(str.isdigit, value))
            return cls(number=cleaned_value)

    # Success case
    try:
        # Valid CUIT with correct format
        valid_cuit = CUITNumber.from_string("20-12345678-9")
        print(f"Success! Valid CUIT: {valid_cuit.number}")  # Output: Success! Valid CUIT: 20123456789
    except ValueError as e:
        print(f"Error: {e}")

    # Error cases
    try:
        # Invalid CUIT (too short)
        invalid_cuit = CUITNumber.from_string("123")
        print("This line won't be reached")
    except ValueError as e:
        print(f"Error: {e}")  # Output: Error: Field number length must be between 11 and 11 characters
    ```

8. **Service Invoice Content Validation**
   * Validates service codes, unit prices, discounts, and VAT rates
   * Different validation rules based on issuer type (Responsable Inscripto vs Monotributo)
   * Automatic calculation of discounts and VAT amounts
   * Strict decimal place handling for financial values

   ```python
   # VAT Rate Validation Examples
   from decimal import Decimal
   from models.invoice_content_services import create_service_invoice_line
   from models.invoice_types import IssuerType

   # Example 1: Standard VAT rate (21%)
   try:
       service = create_service_invoice_line(
           service_code="1234",
           unit_price="1000",
           issuer_type=IssuerType.RESPONSABLE_INSCRIPTO,
           vat_rate="21"    # User inputs 21 for 21% VAT
       )
       print(f"Price with 21% VAT: ${service.total_price}")  # Output: Price with 21% VAT: $1210.00

   # Example 2: Special case - Exempt
   try:
       service = create_service_invoice_line(
           service_code="1234",
           unit_price="1000",
           issuer_type=IssuerType.RESPONSABLE_INSCRIPTO,
           vat_rate="EXENTO"
       )
       print(f"Exempt price: ${service.total_price}")  # Output: Exempt price: $1000.00

   # Example 3: Invalid VAT rate
   try:
       service = create_service_invoice_line(
           service_code="1234",
           unit_price="1000",
           issuer_type=IssuerType.RESPONSABLE_INSCRIPTO,
           vat_rate="15"    # Invalid: 15% is not a valid VAT rate
       )
   except ValueError as e:
       print(f"Error: {e}")  
       # Output: Error: Invalid VAT rate. Valid rates are: 0, 2.5, 5, 10.5, 21, 27%, NO_GRAVADO, or EXENTO
   ```

   **VAT Rate Validation Rules**:
   - Valid percentage inputs:
     - "0" (0%)
     - "2.5" (2.5%)
     - "5" (5%)
     - "10.5" (10.5%)
     - "21" (21%)
     - "27" (27%)
   - Special cases:
     - "NO_GRAVADO" (Not taxed)
     - "EXENTO" (Exempt)
   - Invalid inputs:
     - Any other percentage (e.g., "15")
     - Invalid formats (e.g., "21%", "21.00")
     - Empty or non-numeric values

#### Environment Variables

The following environment variables are validated against these models:

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
     - Issuance date must be within a 21-day window:
       - No more than 10 days in the past
       - No more than 10 days in the future
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
   - Must be compatible with issuer type
   - Responsable Inscripto issuers have limited condition options
   - Monotributo issuers have access to all conditions
   - No default value - must be explicitly set
   - Spanish descriptions maintained for UI consistency
   - Valid codes vary by issuer type:
     - Common codes (both issuer types):
       - "1": IVA Responsable Inscripto
       - "6": Responsable Monotributo
       - "13": Monotributista Social
       - "16": Monotributista Trabajador Independiente Promovido
     - Additional codes (Monotributo only):
       - "4": IVA Sujeto Exento
       - "5": Consumidor Final
       - "7": Sujeto No Categorizado
       - "8": Proveedor del Exterior
       - "9": Cliente del Exterior
       - "10": IVA Liberado - Ley Nº 19.640
       - "15": IVA No Alcanzado

8. **CUIT Number**:
   - Format: Exactly 11 digits
   - Only numeric characters allowed
   - Auto-cleaning: Non-numeric characters are removed
   - Structure (future validation):
     - First 2 digits: Taxpayer type
     - Next 8 digits: Unique identifier
     - Last digit: Verification code
   - Examples:
     - Valid: "20123456789"
     - Invalid: "123" (too short)
     - Invalid: "2012345678A" (contains letter)

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
- Invalid CUIT format
- CUIT length violations
- Non-numeric CUIT characters

### Testing
Test scripts are organized by service and functionality. All tests can be run using `uv run` followed by the script name:

#### 1. Authentication Testing
Tests basic AFIP authentication:
```bash
uv run test_auth
```

#### 2. Comprobantes en línea Service Testing
A series of progressive tests for the invoice generation workflow:

1. Navigation to Invoice Generator:
```bash
uv run test_comp_nav
```
Tests navigation from authentication through service selection to the invoice generator.

2. Invoice Type Selection:
```bash
uv run test_comp_type
```
Tests the punto de venta and invoice type selection process.

3. Form Filling Tests:
```bash
# Test invoice issuance data form
uv run test_comp_form_1

# Test recipient data form
uv run test_comp_form_2

# Test invoice content form
uv run test_comp_form_3
```

Each test builds upon the previous steps, allowing for isolated testing of specific functionality. All tests include verbose output for debugging purposes and run in non-headless mode by default during testing.

Note: All test scripts automatically handle browser setup and cleanup, including proper closing of browser instances after test completion.

### Contribuyente Management
The system provides a CLI command to manage contribuyentes (taxpayers) in the system:

```bash
uv run add_contribuyente --cuit <cuit> --password <password>
```

This command:
- Validates the CUIT format using the existing Pydantic model
- Ensures the CUIT is exactly 11 digits
- Automatically cleans non-numeric characters from the CUIT
- Stores the contribuyente credentials in `src/autoBilanceo/data/contribuyentes.json`

#### Available Options
| Option | Description | Required |
|--------|-------------|----------|
| `--cuit` | 🔢 CUIT number of the contribuyente (11 digits) | Yes |
| `--password` | 🔐 Password for the contribuyente | Yes |

Example usage:
```bash
# Add a new contribuyente
uv run add_contribuyente --cuit 20328619548 --password "myPassword123"

# Success output
✓ Successfully added contribuyente with CUIT: 20328619548

# Error output (invalid CUIT)
⨯ Failed to add contribuyente
Error: Invalid CUIT format - CUIT must contain only numbers
```

The contribuyentes.json file maintains a simple key-value structure:
```json
{
  "20328619548": "myPassword123",
  "27336006614": "anotherPassword"
}
```

### Batch Processing
The system implements intelligent batch processing for multiple invoices, ensuring efficient concurrent processing while maintaining AFIP's session integrity.

#### Batch Processing Rules
- Maximum concurrent processes are configurable (default: 3)
- No concurrent processing of invoices from the same issuer (CUIT)
- Automatic batch size adjustment based on unique issuers
- Configurable delay between batches to avoid overwhelming AFIP servers

#### Batch Processing Scenarios

1. **Single Issuer, Multiple Invoices**
   ```
   Input: 3 invoices from same issuer (CUIT: 20328619548), max_concurrent=3
   Result: 3 batches of 1 invoice each
   - Batch 1: [Invoice 1]
   - Batch 2: [Invoice 2]
   - Batch 3: [Invoice 3]
   ```

2. **Multiple Issuers, Even Distribution**
   ```
   Input: 4 invoices (2 from each issuer), max_concurrent=3
   - Issuer A (CUIT: 20328619548): 2 invoices
   - Issuer B (CUIT: 27336006614): 2 invoices
   
   Result: 2 batches
   - Batch 1: [Invoice A1, Invoice B1]
   - Batch 2: [Invoice A2, Invoice B2]
   ```

3. **Multiple Issuers, Mixed Distribution**
   ```
   Input: 6 invoices total, max_concurrent=3
   - Issuer A (CUIT: 20328619548): 3 invoices
   - Issuer B (CUIT: 27336006614): 2 invoices
   - Issuer C (CUIT: 30715449133): 1 invoice
   
   Result: 3 batches
   - Batch 1: [Invoice A1, Invoice B1, Invoice C1]
   - Batch 2: [Invoice A2, Invoice B2]
   - Batch 3: [Invoice A3]
   ```

This batching strategy ensures:
- Optimal resource utilization
- No CUIT session conflicts
- Predictable processing patterns
- Scalable invoice processing

The batch processor provides detailed logging of batch composition when running in verbose mode, helping track the processing of large invoice sets.
