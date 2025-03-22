from enum import IntEnum
from .invoice_types import IssuerType, InvoiceType
from pydantic import BaseModel, Field, model_validator, field_validator

# TODO: Replace the CUIT validators here and use the generic version from cuit.py

class IVACondition(IntEnum):
    """
    Enum representing different IVA conditions available in AFIP's invoice system
    """
    # Common conditions for FACTURA_A and FACTURA_C
    IVA_RESPONSABLE_INSCRIPTO = 1
    RESPONSABLE_MONOTRIBUTO = 6
    MONOTRIBUTISTA_SOCIAL = 13
    MONOTRIBUTISTA_TRABAJADOR_INDEPENDIENTE_PROMOVIDO = 16

    # Common conditions for FACTURA_C and FACTURA_B
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
    invoice_type: InvoiceType = Field(
        description="Type of invoice getting created"
    )

    @model_validator(mode='after')
    def validate_condition_for_issuer(self) -> 'IVAConditionInfo':
        condition = self.condition
        issuer_type = self.issuer_type
        invoice_type = self.invoice_type

        if issuer_type == IssuerType.RESPONSABLE_INSCRIPTO:
            if invoice_type == InvoiceType.FACTURA_A:
                valid_conditions = {
                    IVACondition.IVA_RESPONSABLE_INSCRIPTO,
                    IVACondition.RESPONSABLE_MONOTRIBUTO,
                    IVACondition.MONOTRIBUTISTA_SOCIAL,
                    IVACondition.MONOTRIBUTISTA_TRABAJADOR_INDEPENDIENTE_PROMOVIDO
                }
            else:
                valid_conditions = {
                    IVACondition.IVA_SUJETO_EXENTO,
                    IVACondition.CONSUMIDOR_FINAL,
                    IVACondition.SUJETO_NO_CATEGORIZADO,
                    IVACondition.PROVEEDOR_DEL_EXTERIOR,
                    IVACondition.CLIENTE_DEL_EXTERIOR,
                    IVACondition.IVA_LIBERADO_LEY_19640,
                    IVACondition.IVA_NO_ALCANZADO,
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
                f'Invalid IVA condition {condition} for issuer type {issuer_type.name} and invoice type {invoice_type.name}'
            )
        return self

# Mapping of IVA condition descriptions
IVA_CONDITION_DESCRIPTIONS = {
    IVACondition.IVA_RESPONSABLE_INSCRIPTO: "IVA Responsable Inscripto",
    IVACondition.RESPONSABLE_MONOTRIBUTO: "Responsable Monotributo",
    IVACondition.MONOTRIBUTISTA_SOCIAL: "Monotributista Social",
    IVACondition.MONOTRIBUTISTA_TRABAJADOR_INDEPENDIENTE_PROMOVIDO: "Monotributista Trabajador Independiente Promovido",
    IVACondition.IVA_SUJETO_EXENTO: "IVA Sujeto Exento",
    IVACondition.CONSUMIDOR_FINAL: "Consumidor Final",
    IVACondition.SUJETO_NO_CATEGORIZADO: "Sujeto No Categorizado",
    IVACondition.PROVEEDOR_DEL_EXTERIOR: "Proveedor del Exterior",
    IVACondition.CLIENTE_DEL_EXTERIOR: "Cliente del Exterior",
    IVACondition.IVA_LIBERADO_LEY_19640: "IVA Liberado - Ley Nº 19.640",
    IVACondition.IVA_NO_ALCANZADO: "IVA No Alcanzado"
}

def create_iva_condition_info(
    condition: IVACondition, issuer_type: IssuerType, invoice_type: InvoiceType
) -> IVAConditionInfo:
    """
    Creates an IVAConditionInfo instance with the specified condition and issuer type

    Args:
        condition: IVA condition of the recipient
        issuer_type: Type of issuer creating the invoice
        invoice:type: Type of invoice getting created

    Returns:
        IVAConditionInfo instance

    Raises:
        ValueError: If the condition is invalid for the given issuer type
    """
    return IVAConditionInfo(
        condition=condition,
        issuer_type=issuer_type,
        invoice_type=invoice_type
    )

