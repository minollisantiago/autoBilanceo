from enum import IntEnum
from typing import Optional, Dict
from .invoice_types import IssuerType
from decimal import Decimal, InvalidOperation
from pydantic import BaseModel, Field, field_validator, model_validator

class IVARateInternal(IntEnum):
    """Internal enum for AFIP's IVA rate codes"""
    NO_GRAVADO = 1
    EXENTO = 2
    CERO = 3
    DOS_CINCO = 9
    CINCO = 8
    DIEZ_CINCO = 4
    VEINTIUNO = 5
    VEINTISIETE = 6

# Mapping between user-input percentages and internal AFIP codes
IVA_RATE_MAPPING = {
    Decimal('0'): IVARateInternal.CERO,
    Decimal('2.5'): IVARateInternal.DOS_CINCO,
    Decimal('5'): IVARateInternal.CINCO,
    Decimal('10.5'): IVARateInternal.DIEZ_CINCO,
    Decimal('21'): IVARateInternal.VEINTIUNO,
    Decimal('27'): IVARateInternal.VEINTISIETE,
    'NO_GRAVADO': IVARateInternal.NO_GRAVADO,
    'EXENTO': IVARateInternal.EXENTO
}

class IVARate(BaseModel):
    """
    Model for validating IVA rates using user-friendly percentage values
    """
    rate: Decimal = Field(
        ...,
        description="IVA rate percentage (e.g., 21 for 21% IVA)"
    )
    internal_code: IVARateInternal = Field(
        description="Internal AFIP code for the IVA rate"
    )

    @classmethod
    def from_string(cls, value: str) -> 'IVARate':
        """
        Creates a IVARate instance from a string input
        Accepts percentage values or special cases (NO_GRAVADO, EXENTO)
        """
        try:
            # Handle special cases
            if value.upper() in ['NO_GRAVADO', 'EXENTO']:
                internal_code = IVA_RATE_MAPPING[value.upper()]
                return cls(rate=Decimal('0'), internal_code=internal_code)

            # Handle percentage values
            rate = Decimal(value)
            if rate not in IVA_RATE_MAPPING:
                valid_rates = [str(rate) for rate in IVA_RATE_MAPPING.keys()
                             if isinstance(rate, Decimal)]
                raise ValueError(
                    f'Invalid IVA rate. Valid rates are: {", ".join(valid_rates)}%, '
                    'NO_GRAVADO, or EXENTO'
                )

            return cls(
                rate=rate,
                internal_code=IVA_RATE_MAPPING[rate]
            )
        except (ValueError, InvalidOperation) as e:
            raise ValueError(f'Invalid IVA rate format: {e}')

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
    def total_price(self) -> Decimal:
        """Calculate final price including IVA if applicable"""
        base_price = self.discounted_price
        if (self.issuer_type == IssuerType.RESPONSABLE_INSCRIPTO
            and self.iva_rate
            and self.iva_rate.rate > 0):
            return base_price * (1 + self.iva_rate.rate / 100)
        return base_price

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
        iva_rate: IVA rate (required for RESPONSABLE_INSCRIPTO, must be None for MONOTRIBUTO)

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
