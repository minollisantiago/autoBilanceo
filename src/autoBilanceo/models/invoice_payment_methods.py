from typing import Set, Dict
from enum import IntEnum
from pydantic import BaseModel, Field

class PaymentMethod(IntEnum):
    """
    Enum representing different payment methods available in AFIP's invoice system
    """
    CONTADO = 1
    TARJETA_DEBITO = 69
    TARJETA_CREDITO = 68
    CUENTA_CORRIENTE = 96
    CHEQUE = 97
    TRANSFERENCIA_BANCARIA = 91
    OTRA = 99
    OTROS_MEDIOS_ELECTRONICOS = 90

# Map PaymentMethod values to their position IDs in the form
PAYMENT_METHOD_FORM_IDS: Dict[PaymentMethod, int] = {
    PaymentMethod.CONTADO: 1,
    PaymentMethod.TARJETA_DEBITO: 2,
    PaymentMethod.TARJETA_CREDITO: 3,
    PaymentMethod.CUENTA_CORRIENTE: 4,
    PaymentMethod.CHEQUE: 5,
    PaymentMethod.TRANSFERENCIA_BANCARIA: 6,
    PaymentMethod.OTRA: 7,
    PaymentMethod.OTROS_MEDIOS_ELECTRONICOS: 8,
}

class PaymentMethodInfo(BaseModel):
    """
    Model for validating payment methods selection
    At least one payment method must be selected
    """
    selected_methods: Set[PaymentMethod] = Field(
        default_factory=set,
        description="Set of selected payment methods"
    )

    def add_payment_method(self, method: PaymentMethod) -> None:
        """Add a payment method to the selected set"""
        self.selected_methods.add(method)

    def remove_payment_method(self, method: PaymentMethod) -> None:
        """Remove a payment method from the selected set"""
        self.selected_methods.discard(method)

    def has_payment_method(self, method: PaymentMethod) -> bool:
        """Check if a specific payment method is selected"""
        return method in self.selected_methods

    @property
    def requires_card_data(self) -> bool:
        """Check if any selected payment method requires additional card data"""
        card_methods = {PaymentMethod.TARJETA_DEBITO, PaymentMethod.TARJETA_CREDITO}
        return any(method in card_methods for method in self.selected_methods)

    def get_form_id(self, method: PaymentMethod) -> int:
        """Get the form ID for a payment method"""
        form_id = PAYMENT_METHOD_FORM_IDS.get(method)
        if form_id is None:
            raise ValueError(f"No form ID mapping found for payment method: {method.name}")
        return form_id

# Mapping of payment method descriptions
PAYMENT_METHOD_DESCRIPTIONS = {
    PaymentMethod.CONTADO: "Contado",
    PaymentMethod.TARJETA_DEBITO: "Tarjeta de Débito",
    PaymentMethod.TARJETA_CREDITO: "Tarjeta de Crédito",
    PaymentMethod.CUENTA_CORRIENTE: "Cuenta Corriente",
    PaymentMethod.CHEQUE: "Cheque",
    PaymentMethod.TRANSFERENCIA_BANCARIA: "Transferencia Bancaria",
    PaymentMethod.OTRA: "Otra",
    PaymentMethod.OTROS_MEDIOS_ELECTRONICOS: "Otros medios de pago electrónico"
}

def create_payment_method_info(*methods: PaymentMethod) -> PaymentMethodInfo:
    """
    Creates a PaymentMethodInfo instance with the specified payment methods

    Args:
        *methods: Variable number of PaymentMethod values to include

    Returns:
        PaymentMethodInfo instance with the specified methods

    Raises:
        ValueError: If no payment methods are provided
    """
    if not methods:
        raise ValueError("At least one payment method must be selected")

    return PaymentMethodInfo(selected_methods=set(methods))

