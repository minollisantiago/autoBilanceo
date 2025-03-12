from enum import IntEnum
from pydantic import BaseModel, Field

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

