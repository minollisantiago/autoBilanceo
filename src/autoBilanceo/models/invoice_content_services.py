from enum import IntEnum
from typing import Optional
from .invoice_types import IssuerType
from decimal import Decimal, InvalidOperation
from pydantic import BaseModel, Field, field_validator, model_validator

class IVARate(IntEnum):
    """
    Enum representing different iva rates available in AFIP's invoice system
    """
    NO_GRAVADO = 1      # No gravado
    EXENTO = 2          # Exento
    CERO = 3            # 0%
    DOS_CINCO = 9       # 2.5%
    CINCO = 8           # 5%
    DIEZ_CINCO = 4      # 10.5%
    VEINTIUNO = 5       # 21%
    VEINTISIETE = 6     # 27%

# Mapping of iva rate descriptions and their decimal values
IVA_RATE_INFO = {
    IVARate.NO_GRAVADO: {"description": "No gravado", "rate": Decimal('0')},
    IVARate.EXENTO: {"description": "Exento", "rate": Decimal('0')},
    IVARate.CERO: {"description": "0%", "rate": Decimal('0')},
    IVARate.DOS_CINCO: {"description": "2,5%", "rate": Decimal('2.5')},
    IVARate.CINCO: {"description": "5%", "rate": Decimal('5')},
    IVARate.DIEZ_CINCO: {"description": "10,5%", "rate": Decimal('10.5')},
    IVARate.VEINTIUNO: {"description": "21%", "rate": Decimal('21')},
    IVARate.VEINTISIETE: {"description": "27%", "rate": Decimal('27')}
}

class ServiceCode(BaseModel):
    """
    Model for validating service codes
    Must be up to 4 digits, numbers only
    Shorter numbers will be padded with leading zeros
    """
    code: str = Field(
        ...,
        min_length=4,
        max_length=4,
        description="Service code - must be exactly 4 digits, smaller numbers are padded with leading zeros"
    )

    @field_validator('code')
    @classmethod
    def validate_service_code(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError('Service code must contain only numbers')
        if len(v) > 4:
            raise ValueError('Service code must be up to 4 digits long')
        return v.zfill(4)

    @classmethod
    def from_string(cls, value: str) -> 'ServiceCode':
        """Creates a ServiceCode instance from a string"""
        cleaned_value = value.strip()
        if not cleaned_value.isdigit():
            raise ValueError('Service code must contain only numbers')
        if len(cleaned_value) > 4:
            raise ValueError('Service code must be up to 4 digits long')
        return cls(code=cleaned_value.zfill(4))

class UnitPrice(BaseModel):
    """
    Model for validating unit prices
    Must be a positive number, allows decimals
    Maximum 19 digits total (including decimals)
    """
    amount: Decimal = Field(
        ...,
        ge=Decimal('0'),
        description="Unit price - must be a positive number with up to 2 decimal places"
    )

    @field_validator('amount')
    @classmethod
    def validate_unit_price(cls, v: Decimal) -> Decimal:
        # Convert to string to check total length including decimal point
        str_value = str(v)
        if len(str_value.replace('.', '')) > 19:
            raise ValueError('Unit price cannot exceed 19 digits in total')

        # Ensure no more than 2 decimal places
        decimal_places = len(str_value.split('.')[-1]) if '.' in str_value else 0
        if decimal_places > 2:
            raise ValueError('Unit price cannot have more than 2 decimal places')

        return v

    @classmethod
    def from_string(cls, value: str) -> 'UnitPrice':
        """Creates a UnitPrice instance from a string"""
        try:
            # Remove any whitespace and convert to Decimal
            cleaned_value = value.strip()
            return cls(amount=Decimal(cleaned_value))
        except (ValueError, InvalidOperation):
            raise ValueError('Invalid unit price format')

class DiscountPercentage(BaseModel):
    """
    Model for validating discount percentages
    Must be a number between 0 and 100
    Maximum 6 digits total (including decimals)
    """
    percentage: Decimal = Field(
        default=Decimal('0'),
        ge=Decimal('0'),
        le=Decimal('100'),
        description="Discount percentage - must be between 0 and 100"
    )

    @field_validator('percentage')
    @classmethod
    def validate_discount_percentage(cls, v: Decimal) -> Decimal:
        # Convert to string to check total length including decimal point
        str_value = str(v)
        if len(str_value.replace('.', '')) > 6:
            raise ValueError('Discount percentage cannot exceed 6 digits in total')

        # Ensure no more than 2 decimal places
        decimal_places = len(str_value.split('.')[-1]) if '.' in str_value else 0
        if decimal_places > 2:
            raise ValueError('Discount percentage cannot have more than 2 decimal places')

        return v

    @classmethod
    def from_string(cls, value: str) -> 'DiscountPercentage':
        """Creates a DiscountPercentage instance from a string"""
        try:
            # Remove any whitespace and convert to Decimal
            cleaned_value = value.strip()
            # If empty or only whitespace, use default 0
            if not cleaned_value:
                return cls(percentage=Decimal('0'))
            return cls(percentage=Decimal(cleaned_value))
        except (ValueError, InvalidOperation):
            raise ValueError('Invalid discount percentage format')

class ServiceInvoiceLine(BaseModel):
    """
    Model for validating a complete service invoice line
    Structure varies based on issuer type
    """
    issuer_type: IssuerType
    service_code: ServiceCode
    unit_price: UnitPrice
    discount_percentage: DiscountPercentage = DiscountPercentage(percentage=Decimal('0'))
    iva_rate: Optional[IVARate] = None

    @model_validator(mode='after')
    def validate_iva_rate_for_issuer(self) -> 'ServiceInvoiceLine':
        if self.issuer_type == IssuerType.RESPONSABLE_INSCRIPTO and self.iva_rate is None:
            raise ValueError('iva rate is required for Responsable Inscripto')
        elif self.issuer_type == IssuerType.MONOTRIBUTO and self.iva_rate is not None:
            raise ValueError('iva rate should not be specified for Monotributo')
        return self

    @property
    def discounted_price(self) -> Decimal:
        """Calculate the price after applying the discount"""
        if self.discount_percentage.percentage == 0:
            return self.unit_price.amount

        discount_multiplier = (100 - self.discount_percentage.percentage) / 100
        return self.unit_price.amount * discount_multiplier

    @property
    def iva_amount(self) -> Decimal:
        """Calculate the iva amount if applicable"""
        if self.issuer_type == IssuerType.MONOTRIBUTO or self.iva_rate is None:
            return Decimal('0')

        rate = IVA_RATE_INFO[self.iva_rate]['rate']
        return self.discounted_price * (rate / 100)

    @property
    def total_price(self) -> Decimal:
        """Calculate the total price including iva if applicable"""
        return self.discounted_price + self.iva_amount

def create_service_invoice_line(
    issuer_type: IssuerType,
    service_code: str,
    unit_price: str,
    discount_percentage: Optional[str] = None,
    iva_rate: Optional[IVARate] = None
) -> ServiceInvoiceLine:
    """
    Creates a ServiceInvoiceLine instance with the specified values

    Args:
        issuer_type: Type of issuer (RESPONSABLE_INSCRIPTO or MONOTRIBUTO)
        service_code: 4-digit service code
        unit_price: Price amount as string
        discount_percentage: Optional discount percentage as string
        iva_rate: iva rate (required for RESPONSABLE_INSCRIPTO, must be None for MONOTRIBUTO)

    Returns:
        ServiceInvoiceLine instance

    Raises:
        ValueError: If any of the input values are invalid
    """
    code = ServiceCode.from_string(service_code)
    price = UnitPrice.from_string(unit_price)
    discount = DiscountPercentage.from_string(discount_percentage if discount_percentage is not None else "0")

    return ServiceInvoiceLine(
        issuer_type=issuer_type,
        service_code=code,
        unit_price=price,
        discount_percentage=discount,
        iva_rate=iva_rate
    )
