from pydantic import BaseModel, Field, field_validator

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

