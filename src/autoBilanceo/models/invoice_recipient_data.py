from typing import Dict
from enum import IntEnum
from .invoice_types import IssuerType
from pydantic import BaseModel, Field, field_validator

class IVACondition(IntEnum):
    """
    Enum representing different IVA conditions available in AFIP's invoice system
    """
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
    """
    Model for validating IVA condition
    """
    condition: IVACondition = Field(
        description="IVA condition of the invoice recipient"
    )
    issuer_type: IssuerType = Field(
        description="Type of issuer creating the invoice"
    )

    @field_validator('condition', mode='before')
    @classmethod
    def validate_condition_for_issuer(cls, value: Dict) -> IVACondition:
        condition = value.get('condition')
        issuer_type = value.get('issuer_type')

        if issuer_type is None:
            raise ValueError('Issuer type must be provided')

        if issuer_type == IssuerType.RESPONSABLE_INSCRIPTO:
            valid_conditions = {
                IVACondition.IVA_RESPONSABLE_INSCRIPTO,
                IVACondition.RESPONSABLE_MONOTRIBUTO,
                IVACondition.MONOTRIBUTISTA_SOCIAL,
                IVACondition.MONOTRIBUTISTA_TRABAJADOR_INDEPENDIENTE_PROMOVIDO
            }
        else:  # MONOTRIBUTO
            valid_conditions = {
                IVACondition.IVA_RESPONSABLE_INSCRIPTO,
                IVACondition.IVA_SUJETO_EXENTO,
                IVACondition.CONSUMIDOR_FINAL,
                IVACondition.RESPONSABLE_MONOTRIBUTO,
                IVACondition.SUJETO_NO_CATEGORIZADO,
                IVACondition.PROVEEDOR_DEL_EXTERIOR,
                IVACondition.CLIENTE_DEL_EXTERIOR,
                IVACondition.IVA_LIBERADO_LEY_19640,
                IVACondition.MONOTRIBUTISTA_SOCIAL,
                IVACondition.IVA_NO_ALCANZADO,
                IVACondition.MONOTRIBUTISTA_TRABAJADOR_INDEPENDIENTE_PROMOVIDO
            }

        if condition not in valid_conditions:
            raise ValueError(
                f'Invalid IVA condition {condition} for issuer type {issuer_type.name}'
            )
        return condition

# Mapping of IVA condition descriptions
IVA_CONDITION_DESCRIPTIONS = {
    # Common conditions
    IVACondition.IVA_RESPONSABLE_INSCRIPTO: "IVA Responsable Inscripto",
    IVACondition.RESPONSABLE_MONOTRIBUTO: "Responsable Monotributo",
    IVACondition.MONOTRIBUTISTA_SOCIAL: "Monotributista Social",
    IVACondition.MONOTRIBUTISTA_TRABAJADOR_INDEPENDIENTE_PROMOVIDO: "Monotributista Trabajador Independiente Promovido",

    # Additional conditions for MONOTRIBUTO
    IVACondition.IVA_SUJETO_EXENTO: "IVA Sujeto Exento",
    IVACondition.CONSUMIDOR_FINAL: "Consumidor Final",
    IVACondition.SUJETO_NO_CATEGORIZADO: "Sujeto No Categorizado",
    IVACondition.PROVEEDOR_DEL_EXTERIOR: "Proveedor del Exterior",
    IVACondition.CLIENTE_DEL_EXTERIOR: "Cliente del Exterior",
    IVACondition.IVA_LIBERADO_LEY_19640: "IVA Liberado - Ley Nº 19.640",
    IVACondition.IVA_NO_ALCANZADO: "IVA No Alcanzado"
}

def create_iva_condition_info(condition: IVACondition, issuer_type: IssuerType) -> IVAConditionInfo:
    """
    Creates an IVAConditionInfo instance with the specified condition and issuer type

    Args:
        condition: IVA condition of the recipient
        issuer_type: Type of issuer creating the invoice

    Returns:
        IVAConditionInfo instance

    Raises:
        ValueError: If the condition is invalid for the given issuer type
    """
    return IVAConditionInfo(condition=condition, issuer_type=issuer_type)

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

