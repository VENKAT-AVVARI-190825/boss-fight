from app import db
from app.models import Currency, CurrencyRate


CURRENCIES = [
    {"id": 1, "currency_code": "INR", "currency_name": "Indian Rupees",     "country_name": "INDIA"},
    {"id": 2, "currency_code": "USD", "currency_name": "US Dollars",        "country_name": "USA"},
    {"id": 3, "currency_code": "CAD", "currency_name": "Canadian Dollars",  "country_name": "CANADA"},
    {"id": 4, "currency_code": "EUR", "currency_name": "European Dollars",  "country_name": "EUROPE"},
    {"id": 5, "currency_code": "AUD", "currency_name": "Australian Dollars","country_name": "AUSTRALIA"},
    {"id": 6, "currency_code": "AED", "currency_name": "UAE Dirham",        "country_name": "UAE"},
]

RATES = [
    {"currency_code_from": "USD", "currency_code_to": "INR", "exchange_rate": 80.08},
    {"currency_code_from": "CAD", "currency_code_to": "INR", "exchange_rate": 61.62},
    {"currency_code_from": "USD", "currency_code_to": "CAD", "exchange_rate": 1.36},
    {"currency_code_from": "EUR", "currency_code_to": "INR", "exchange_rate": 93.14},
    {"currency_code_from": "AUD", "currency_code_to": "INR", "exchange_rate": 56.81},
    {"currency_code_from": "AED", "currency_code_to": "INR", "exchange_rate": 22.79},
]


def seed_database() -> None:
    for data in CURRENCIES:
        if not Currency.query.filter_by(currency_code=data["currency_code"]).first():
            db.session.add(Currency(**data))

    db.session.flush()

    for data in RATES:
        if not CurrencyRate.query.filter_by(
            currency_code_from=data["currency_code_from"],
            currency_code_to=data["currency_code_to"],
        ).first():
            db.session.add(CurrencyRate(**data))

    db.session.commit()
    print("Database seeded successfully.")
