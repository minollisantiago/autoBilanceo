from enum import StrEnum
from pydantic import BaseModel

class CurrencyCode(StrEnum):
    """
    Enum representing different currency codes available for invoicing in AFIP's system
    """
    # Special value for unselected state
    UNSELECTED = ""

    # Asian Currencies
    BAHT_TAILANDIA = "057"
    DOLAR_HONG_KONG = "051"
    DOLAR_SINGAPUR = "052"
    DOLAR_TAIWAN = "054"
    YUAN_CHINA = "064"
    RUPIA_HINDU = "062"
    YEN_JAPONES = "019"
    DINAR_KUWAITI = "059"

    # European Currencies
    EURO = "060"
    CORONA_CHECA = "024"
    CORONA_DANESA = "014"
    CORONA_NORUEGA = "015"
    CORONA_SUECA = "016"
    DINAR_SERBIO = "025"
    FRANCO_SUIZO = "009"
    FORINT_HUNGRIA = "056"
    LEU_RUMANO = "040"
    LIBRA_ESTERLINA = "021"
    ZLOTY_POLACO = "061"
    RUBLO_RUSIA = "RUB"

    # North American Currencies
    DOLAR_ESTADOUNIDENSE = "DOL"
    DOLAR_LIBRE_EEUU = "002"
    DOLAR_CANADIENSE = "018"
    PESO_MEXICANO = "010"

    # Central American and Caribbean Currencies
    BALBOA_PANAMENA = "043"
    CORDOBA_NICARAGUENSE = "044"
    DOLAR_JAMAICA = "053"
    FLORIN_ANTILLAS_HOLANDESAS = "028"
    LEMPIRA_HONDURENA = "063"
    PESO_DOMINICANO = "042"
    QUETZAL_GUATEMALTECO = "055"

    # South American Currencies
    BOLIVAR_VENEZOLANO = "023"
    GUARANI_PARAGUAYO = "029"
    NUEVO_SOL_PERUANO = "035"
    PESO_BOLIVIANO = "031"
    PESO_CHILENO = "033"
    PESO_COLOMBIANO = "032"
    PESO_URUGUAYO = "011"
    REAL_BRASILENO = "012"

    # Oceania Currencies
    DOLAR_AUSTRALIANO = "026"
    DOLAR_NEOZELANDES = "NZD"

    # African and Middle Eastern Currencies
    DIRHAM_MARROQUI = "045"
    LIBRA_EGIPCIA = "046"
    RAND_SUDAFRICANO = "034"
    RIYAL_SAUDITA = "047"
    SHEKEL_ISRAEL = "030"

    # Special Units
    DERECHOS_ESPECIALES_GIRO = "041"
    GRAMOS_ORO_FINO = "049"

class CurrencyInfo(BaseModel):
    """
    Pydantic model representing currency information
    """
    code: CurrencyCode
    description: str

# Mapping of currency descriptions
CURRENCY_DESCRIPTIONS = {
    # Asian Currencies
    CurrencyCode.BAHT_TAILANDIA: "Baht (Tailandia)",
    CurrencyCode.DOLAR_HONG_KONG: "Dólar de Hong Kong",
    CurrencyCode.DOLAR_SINGAPUR: "Dólar de Singapur",
    CurrencyCode.DOLAR_TAIWAN: "Dólar de Taiwan",
    CurrencyCode.YUAN_CHINA: "Yuan (Rep. Pop. China)",
    CurrencyCode.RUPIA_HINDU: "Rupia Hindú",
    CurrencyCode.YEN_JAPONES: "Yens",
    CurrencyCode.DINAR_KUWAITI: "Dinar Kuwaiti",

    # European Currencies
    CurrencyCode.EURO: "Euro",
    CurrencyCode.CORONA_CHECA: "Corona Checa",
    CurrencyCode.CORONA_DANESA: "Coronas Danesas",
    CurrencyCode.CORONA_NORUEGA: "Coronas Noruegas",
    CurrencyCode.CORONA_SUECA: "Coronas Suecas",
    CurrencyCode.DINAR_SERBIO: "Dinar Serbio",
    CurrencyCode.FRANCO_SUIZO: "Franco Suizo",
    CurrencyCode.FORINT_HUNGRIA: "Forint (Hungría)",
    CurrencyCode.LEU_RUMANO: "Leu Rumano",
    CurrencyCode.LIBRA_ESTERLINA: "Libra Esterlina",
    CurrencyCode.ZLOTY_POLACO: "Zloty Polaco",
    CurrencyCode.RUBLO_RUSIA: "Rublo (Rusia)",

    # North American Currencies
    CurrencyCode.DOLAR_ESTADOUNIDENSE: "Dólar Estadounidense",
    CurrencyCode.DOLAR_LIBRE_EEUU: "Dólar Libre EEUU",
    CurrencyCode.DOLAR_CANADIENSE: "Dólar Canadiense",
    CurrencyCode.PESO_MEXICANO: "Pesos Mejicanos",

    # Central American and Caribbean Currencies
    CurrencyCode.BALBOA_PANAMENA: "Balboas Panameñas",
    CurrencyCode.CORDOBA_NICARAGUENSE: "Córdoba Nicaragüense",
    CurrencyCode.DOLAR_JAMAICA: "Dólar de Jamaica",
    CurrencyCode.FLORIN_ANTILLAS_HOLANDESAS: "Florín (Antillas Holandesas)",
    CurrencyCode.LEMPIRA_HONDURENA: "Lempira Hondureña",
    CurrencyCode.PESO_DOMINICANO: "Peso Dominicano",
    CurrencyCode.QUETZAL_GUATEMALTECO: "Quetzal Guatemalteco",

    # South American Currencies
    CurrencyCode.BOLIVAR_VENEZOLANO: "Bolívar Venezolano",
    CurrencyCode.GUARANI_PARAGUAYO: "Güaraní",
    CurrencyCode.NUEVO_SOL_PERUANO: "Nuevo Sol Peruano",
    CurrencyCode.PESO_BOLIVIANO: "Peso Boliviano",
    CurrencyCode.PESO_CHILENO: "Peso Chileno",
    CurrencyCode.PESO_COLOMBIANO: "Peso Colombiano",
    CurrencyCode.PESO_URUGUAYO: "Pesos Uruguayos",
    CurrencyCode.REAL_BRASILENO: "Real",

    # Oceania Currencies
    CurrencyCode.DOLAR_AUSTRALIANO: "Dólar Australiano",
    CurrencyCode.DOLAR_NEOZELANDES: "Dólar Neozelandes",

    # African and Middle Eastern Currencies
    CurrencyCode.DIRHAM_MARROQUI: "Dirham Marroquí",
    CurrencyCode.LIBRA_EGIPCIA: "Libra Egipcia",
    CurrencyCode.RAND_SUDAFRICANO: "Rand Sudafricano",
    CurrencyCode.RIYAL_SAUDITA: "Riyal Saudita",
    CurrencyCode.SHEKEL_ISRAEL: "Shekel (Israel)",

    # Special Units
    CurrencyCode.DERECHOS_ESPECIALES_GIRO: "Derechos Especiales de Giro",
    CurrencyCode.GRAMOS_ORO_FINO: "Gramos de Oro Fino",
}

def create_currency_info(code: CurrencyCode) -> CurrencyInfo:
    """
    Creates a CurrencyInfo instance for the given currency code
    """
    if code == CurrencyCode.UNSELECTED:
        raise ValueError("Currency must be selected")

    return CurrencyInfo(
        code=code,
        description=CURRENCY_DESCRIPTIONS[code]
    )

