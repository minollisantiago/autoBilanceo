from enum import IntEnum
from pydantic import BaseModel, Field, field_validator

class IVACondition(IntEnum):
    """
    Enum representing different IVA conditions available in AFIP's invoice system
    """
    IVA_RESPONSABLE_INSCRIPTO = 1
    RESPONSABLE_MONOTRIBUTO = 6
    MONOTRIBUTISTA_SOCIAL = 13
    MONOTRIBUTISTA_TRABAJADOR_INDEPENDIENTE_PROMOVIDO = 16

class IVAConditionInfo(BaseModel):
    """
    Model for validating IVA condition
    """
    condition: IVACondition = Field(
        description="IVA condition of the invoice recipient"
    )

# Mapping of IVA condition descriptions
IVA_CONDITION_DESCRIPTIONS = {
    IVACondition.IVA_RESPONSABLE_INSCRIPTO: "IVA Responsable Inscripto",
    IVACondition.RESPONSABLE_MONOTRIBUTO: "Responsable Monotributo",
    IVACondition.MONOTRIBUTISTA_SOCIAL: "Monotributista Social",
    IVACondition.MONOTRIBUTISTA_TRABAJADOR_INDEPENDIENTE_PROMOVIDO: "Monotributista Trabajador Independiente Promovido"
}

def create_iva_condition_info(condition: IVACondition) -> IVAConditionInfo:
    """
    Creates an IVAConditionInfo instance with the specified condition

    Args:
        condition: IVA condition of the recipient

    Returns:
        IVAConditionInfo instance

    Raises:
        ValueError: If the condition is invalid
    """
    return IVAConditionInfo(condition=condition)

class CUITNumber(BaseModel):
    """
    Model for validating CUIT (Código Único de Identificación Tributaria)
    Must be exactly 11 digits, numbers only
    """
    number: str = Field(..., min_length=11, max_length=11)

    @field_validator('number')
    @classmethod
    def validate_cuit_format(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError('CUIT must contain only numbers')
        if len(v) != 11:
            raise ValueError('CUIT must be exactly 11 digits long')
        return v

    @classmethod
    def from_string(cls, value: str) -> 'CUITNumber':
        """
        Creates a CUITNumber instance from a string
        Removes any non-numeric characters before validation
        """
        # Remove any non-numeric characters
        cleaned_value = ''.join(filter(str.isdigit, value))
        return cls(number=cleaned_value)

def create_cuit_number(cuit: str) -> CUITNumber:
    """
    Creates a CUITNumber instance with the specified CUIT

    Args:
        cuit: CUIT number as string (11 digits)

    Returns:
        CUITNumber instance

    Raises:
        ValueError: If the CUIT format is invalid
    """
    return CUITNumber.from_string(cuit)

