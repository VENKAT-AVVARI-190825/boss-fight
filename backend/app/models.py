from app import db


class Currency(db.Model):
    __tablename__ = "currency"

    id = db.Column(db.Integer, primary_key=True)
    currency_code = db.Column(db.String(10), unique=True, nullable=False)
    currency_name = db.Column(db.String(100), nullable=False)
    country_name = db.Column(db.String(100), nullable=False)

    def to_dict(self) -> dict:
        return {
            "currencyCode": self.currency_code,
            "currencyName": self.currency_name,
            "countryName": self.country_name,
        }


class CurrencyRate(db.Model):
    __tablename__ = "currency_rate"

    id = db.Column(db.Integer, primary_key=True)
    currency_code_from = db.Column(
        db.String(10), db.ForeignKey("currency.currency_code"), nullable=False
    )
    currency_code_to = db.Column(
        db.String(10), db.ForeignKey("currency.currency_code"), nullable=False
    )
    exchange_rate = db.Column(db.Float, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("currency_code_from", "currency_code_to", name="uq_currency_pair"),
    )

    def to_dict(self) -> dict:
        return {
            "fromCurrencyCode": self.currency_code_from,
            "toCurrencyCode": self.currency_code_to,
            "exchangeRate": str(self.exchange_rate),
        }
