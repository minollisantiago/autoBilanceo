from enum import IntEnum
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, field_validator, model_validator

class ConceptType(IntEnum):
    """
    Enum representing different types of concepts that can be included in an invoice
    """
    PRODUCTOS = 1
    SERVICIOS = 2
    PRODUCTOS_Y_SERVICIOS = 3

class AFIPDate(BaseModel):
    """
    Base model for validating dates in AFIP's dd/mm/yyyy format
    """
    date: datetime

    @field_validator('date')
    @classmethod
    def validate_date_format(cls, v: datetime) -> datetime:
        # Check if date is after year 2000
        if v < datetime(2000, 1, 1):
            raise ValueError('Date must be after year 2000')
        return v

    def format_for_afip(self) -> str:
        """Returns the date in AFIP's required format (dd/mm/yyyy)"""
        return self.date.strftime("%d/%m/%Y")

    @classmethod
    def from_string(cls, value: str) -> 'AFIPDate':
        """
        Creates an AFIPDate instance from a string in dd/mm/yyyy format
        """
        try:
            parsed_date = datetime.strptime(value, "%d/%m/%Y")
            return cls(date=parsed_date)
        except ValueError as e:
            raise ValueError(f'Date: {value} must be in dd/mm/yyyy format - msg: {e}')

class IssuanceDate(BaseModel):
    """
    Model for validating invoice issuance dates with specific rules
    """
    issuance_date: AFIPDate

    @model_validator(mode='after')
    def validate_issuance_window(self) -> 'IssuanceDate':
        """
        Validates that issuance date is within the 10-day window
        """
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        ten_days_ago = today - timedelta(days=10)
        ten_days_ahead = today + timedelta(days=10)

        if self.issuance_date.date < ten_days_ago:
            raise ValueError('Issuance date cannot be more than 10 days in the past')

        if self.issuance_date.date > ten_days_ahead:
            raise ValueError('Issuance date cannot be more than 10 days in the future')

        return self

class BillingPeriod(BaseModel):
    """
    Model representing a billing period with start date, end date, and payment due date
    """
    start_date: AFIPDate
    end_date: AFIPDate
    payment_due_date: AFIPDate

    @model_validator(mode='after')
    def validate_date_ranges(self) -> 'BillingPeriod':
        """
        Validates that:
        1. end_date is not before start_date
        2. payment_due_date is not before end_date
        3. payment_due_date is not before today
        4. start_date is not after today
        """
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

class IssuanceData(BaseModel):
    """
    Main model for invoice issuance data
    """
    issuance_date: IssuanceDate
    concept_type: ConceptType
    billing_period: Optional[BillingPeriod] = None

    @model_validator(mode='after')
    def validate_billing_period_requirement(self) -> 'IssuanceData':
        """
        Validates that billing period is provided when concept includes services
        """
        services_concepts = {ConceptType.SERVICIOS, ConceptType.PRODUCTOS_Y_SERVICIOS}
        if self.concept_type in services_concepts and self.billing_period is None:
            raise ValueError('Billing period is required when concept includes services')
        return self

# Mapping of concept descriptions
CONCEPT_DESCRIPTIONS = {
    ConceptType.PRODUCTOS: "Productos",
    ConceptType.SERVICIOS: "Servicios",
    ConceptType.PRODUCTOS_Y_SERVICIOS: "Productos y Servicios",
}

def create_issuance_data(
    issuance_date: str,
    concept_type: ConceptType,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    payment_due_date: Optional[str] = None
) -> Optional[IssuanceData]:
    """
    Creates an IssuanceData instance with optional billing period

    Args:
        issuance_date: Date in dd/mm/yyyy format
        concept_type: Type of concept being invoiced
        start_date: Optional billing period start date (dd/mm/yyyy)
        end_date: Optional billing period end date (dd/mm/yyyy)
        payment_due_date: Optional payment due date (dd/mm/yyyy)
    """
    try:
        issuance_date_obj = IssuanceDate(
            issuance_date=AFIPDate.from_string(issuance_date)
        )

        # Create billing period if dates are provided
        billing_period = None
        if start_date and end_date and payment_due_date:
            billing_period = BillingPeriod(
                start_date=AFIPDate.from_string(start_date),
                end_date=AFIPDate.from_string(end_date),
                payment_due_date=AFIPDate.from_string(payment_due_date)
            )

        return IssuanceData(
            issuance_date=issuance_date_obj,
            concept_type=concept_type,
            billing_period=billing_period
        )

    except ValueError as e:
        print(f"Invalid issuance data: {e}")
        return None

