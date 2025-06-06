from typing import Optional
from enum import IntEnum, auto
from pydantic import BaseModel, Field, field_validator

class IssuerType(IntEnum):
    """
    Enum representing different types of issuers in the AFIP system
    """
    RESPONSABLE_INSCRIPTO = auto()
    MONOTRIBUTO = auto()

class PuntoVenta(BaseModel):

    #TODO: Needs an extra validation step that checks that the input is amongst the select options

    """
    Model for validating Punto de Venta number
    Must be up to 5 digits, numbers only
    Shorter numbers will be padded with leading zeros
    """
    number: str = Field(..., min_length=5, max_length=5)

    @field_validator('number')
    @classmethod
    def validate_punto_venta(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError('Punto de venta must contain only numbers')
        if len(v) > 5:
            raise ValueError('Punto de venta must be up to 5 digits long')
        return v.zfill(5)

    @classmethod
    def from_string(cls, value: str) -> 'PuntoVenta':
        # Pad with leading zeros if necessary
        padded_value = value.zfill(5)
        return cls(number=padded_value)

class InvoiceType(IntEnum):
    """
    Enum representing different types of invoices available from AFIP's Comprobantes en Linea service.
    """
    # Monotributo Invoice Types
    FACTURA_C = 2
    NOTA_DEBITO_C = 3
    NOTA_CREDITO_C = 4
    RECIBO_C = 5

    # Responsable Inscripto Invoice Types
    FACTURA_A = 10
    NOTA_DEBITO_A = 11
    NOTA_CREDITO_A = 12
    RECIBO_A = 13
    FACTURA_B = 19
    NOTA_DEBITO_B = 21
    NOTA_CREDITO_B = 23
    RECIBO_B = 25
    FACTURA_T = 111
    NOTA_DEBITO_T = 112
    NOTA_CREDITO_T = 113

    # MIPYME Invoice Types - Responsable Inscripto
    FACTURA_CREDITO_ELECTRONICA_MIPYME_A = 114
    NOTA_DEBITO_ELECTRONICA_MIPYME_A = 115
    NOTA_CREDITO_ELECTRONICA_MIPYME_A = 116
    FACTURA_CREDITO_ELECTRONICA_MIPYME_B = 117
    NOTA_DEBITO_ELECTRONICA_MIPYME_B = 118
    NOTA_CREDITO_ELECTRONICA_MIPYME_B = 119

    # MIPYME Invoice Types - Monotributo
    FACTURA_CREDITO_ELECTRONICA_MIPYME_C = 120
    NOTA_DEBITO_ELECTRONICA_MIPYME_C = 121
    NOTA_CREDITO_ELECTRONICA_MIPYME_C = 122

class InvoiceTypeInfo(BaseModel):
    """
    Pydantic model representing invoice type information
    """
    code: InvoiceType
    description: str
    issuer_type: IssuerType
    punto_venta: PuntoVenta

# Mapping of invoice descriptions
INVOICE_TYPE_DESCRIPTIONS = {
    # Monotributo Invoice Types
    InvoiceType.FACTURA_C: "Factura C",
    InvoiceType.NOTA_DEBITO_C: "Nota de Débito C",
    InvoiceType.NOTA_CREDITO_C: "Nota de Crédito C",
    InvoiceType.RECIBO_C: "Recibo C",
    InvoiceType.FACTURA_CREDITO_ELECTRONICA_MIPYME_C: "Factura de Crédito Electrónica MiPyMEs (FCE) C",
    InvoiceType.NOTA_DEBITO_ELECTRONICA_MIPYME_C: "Nota de Débito Electrónica MiPyMEs (FCE) C",
    InvoiceType.NOTA_CREDITO_ELECTRONICA_MIPYME_C: "Nota de Crédito Electrónica MiPyMEs (FCE) C",

    # Responsable Inscripto Invoice Types
    InvoiceType.FACTURA_A: "Factura A",
    InvoiceType.NOTA_DEBITO_A: "Nota de Débito A",
    InvoiceType.NOTA_CREDITO_A: "Nota de Crédito A",
    InvoiceType.RECIBO_A: "Recibo A",
    InvoiceType.FACTURA_B: "Factura B",
    InvoiceType.NOTA_DEBITO_B: "Nota de Débito B",
    InvoiceType.NOTA_CREDITO_B: "Nota de Crédito B",
    InvoiceType.RECIBO_B: "Recibo B",
    InvoiceType.FACTURA_T: "Factura T",
    InvoiceType.NOTA_DEBITO_T: "Nota de Débito T",
    InvoiceType.NOTA_CREDITO_T: "Nota de Crédito T",
    InvoiceType.FACTURA_CREDITO_ELECTRONICA_MIPYME_A: "Factura de Crédito Electrónica MiPyMEs (FCE) A",
    InvoiceType.NOTA_DEBITO_ELECTRONICA_MIPYME_A: "Nota de Débito Electrónica MiPyMEs (FCE) A",
    InvoiceType.NOTA_CREDITO_ELECTRONICA_MIPYME_A: "Nota de Crédito Electrónica MiPyMEs (FCE) A",
    InvoiceType.FACTURA_CREDITO_ELECTRONICA_MIPYME_B: "Factura de Crédito Electrónica MiPyMEs (FCE) B",
    InvoiceType.NOTA_DEBITO_ELECTRONICA_MIPYME_B: "Nota de Débito Electrónica MiPyMEs (FCE) B",
    InvoiceType.NOTA_CREDITO_ELECTRONICA_MIPYME_B: "Nota de Crédito Electrónica MiPyMEs (FCE) B",
}

# Mapping of allowed invoice types per issuer type
ALLOWED_INVOICE_TYPES = {
    IssuerType.MONOTRIBUTO: {
        InvoiceType.FACTURA_C,
        InvoiceType.NOTA_DEBITO_C,
        InvoiceType.NOTA_CREDITO_C,
        InvoiceType.RECIBO_C,
        InvoiceType.FACTURA_CREDITO_ELECTRONICA_MIPYME_C,
        InvoiceType.NOTA_DEBITO_ELECTRONICA_MIPYME_C,
        InvoiceType.NOTA_CREDITO_ELECTRONICA_MIPYME_C,
    },
    IssuerType.RESPONSABLE_INSCRIPTO: {
        InvoiceType.FACTURA_A,
        InvoiceType.NOTA_DEBITO_A,
        InvoiceType.NOTA_CREDITO_A,
        InvoiceType.RECIBO_A,
        InvoiceType.FACTURA_B,
        InvoiceType.NOTA_DEBITO_B,
        InvoiceType.NOTA_CREDITO_B,
        InvoiceType.RECIBO_B,
        InvoiceType.FACTURA_T,
        InvoiceType.NOTA_DEBITO_T,
        InvoiceType.NOTA_CREDITO_T,
        InvoiceType.FACTURA_CREDITO_ELECTRONICA_MIPYME_A,
        InvoiceType.NOTA_DEBITO_ELECTRONICA_MIPYME_A,
        InvoiceType.NOTA_CREDITO_ELECTRONICA_MIPYME_A,
        InvoiceType.FACTURA_CREDITO_ELECTRONICA_MIPYME_B,
        InvoiceType.NOTA_DEBITO_ELECTRONICA_MIPYME_B,
        InvoiceType.NOTA_CREDITO_ELECTRONICA_MIPYME_B,
    }
}

def validate_invoice_type_for_issuer(invoice_type: InvoiceType, issuer_type: IssuerType) -> bool:
    """
    Validates if the given invoice type is allowed for the specified issuer type
    """
    return invoice_type in ALLOWED_INVOICE_TYPES[issuer_type]

def create_invoice_type_info(
    code: InvoiceType,
    issuer_type: IssuerType,
    punto_venta: str
) -> Optional[InvoiceTypeInfo]:
    """
    Creates an InvoiceTypeInfo instance if the invoice type is valid for the given issuer type
    and punto de venta is valid
    """
    if validate_invoice_type_for_issuer(code, issuer_type):
        try:
            pv = PuntoVenta.from_string(punto_venta)
            return InvoiceTypeInfo(
                code=code,
                description=INVOICE_TYPE_DESCRIPTIONS[code],
                issuer_type=issuer_type,
                punto_venta=pv
            )
        except ValueError as e:
            print(f"Invalid punto de venta: {e}")
            return None
    return None
