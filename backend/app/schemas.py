from pydantic import BaseModel, field_validator

from config import Config

ALLOWED_CURRENCIES = Config.ALLOWED_CURRENCIES


class ExchangeRateRequest(BaseModel):
    from_currency: str
    to_currency: str

    @field_validator("from_currency", "to_currency")
    @classmethod
    def must_be_allowed(cls, v: str) -> str:
        code = v.upper()
        if code not in ALLOWED_CURRENCIES:
            raise ValueError(
                f"Currency '{v}' is not supported. Allowed: {', '.join(sorted(ALLOWED_CURRENCIES))}"
            )
        return code

    @field_validator("to_currency")
    @classmethod
    def must_differ(cls, v: str, info) -> str:
        from_cur = info.data.get("from_currency")
        if from_cur and v == from_cur:
            raise ValueError("from_currency and to_currency must be different.")
        return v


class ExchangeRateResponse(BaseModel):
    fromCurrencyCode: str
    toCurrencyCode: str
    exchangeRate: str


class CurrencySchema(BaseModel):
    model_config = {"from_attributes": True}

    currencyCode: str
    currencyName: str
    countryName: str
