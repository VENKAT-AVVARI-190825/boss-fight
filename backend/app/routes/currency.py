from flask import Blueprint, jsonify
from pydantic import ValidationError

from app.models import Currency, CurrencyRate
from app.schemas import ALLOWED_CURRENCIES, ExchangeRateRequest

currency_bp = Blueprint("currency", __name__)


@currency_bp.get("/currency")
def list_currencies() -> tuple:
    """Return all supported currencies keyed by currency code."""
    currencies = Currency.query.filter(
        Currency.currency_code.in_(ALLOWED_CURRENCIES)
    ).all()
    result = {c.currency_code: c.to_dict() for c in currencies}
    return jsonify(result), 200


@currency_bp.get("/exchange-rate/<string:from_cur>/<string:to_cur>")
def get_exchange_rate(from_cur: str, to_cur: str) -> tuple:
    """Return exchange rate between two currencies; computes inverse if needed."""
    try:
        req = ExchangeRateRequest(from_currency=from_cur, to_currency=to_cur)
    except ValidationError as exc:
        errors = [e["msg"] for e in exc.errors()]
        return jsonify({"error": errors[0]}), 400

    from_code = req.from_currency
    to_code = req.to_currency

    # Direct lookup
    rate_row = CurrencyRate.query.filter_by(
        currency_code_from=from_code, currency_code_to=to_code
    ).first()

    if rate_row:
        return jsonify(rate_row.to_dict()), 200

    # Inverse lookup
    inverse_row = CurrencyRate.query.filter_by(
        currency_code_from=to_code, currency_code_to=from_code
    ).first()

    if inverse_row:
        inverse_rate = round(1 / inverse_row.exchange_rate, 6)
        return jsonify(
            {
                "fromCurrencyCode": from_code,
                "toCurrencyCode": to_code,
                "exchangeRate": str(inverse_rate),
            }
        ), 200

    # Try bridging through INR as a common base
    rate_from_inr = _get_rate_via_inr(from_code, to_code)
    if rate_from_inr:
        return jsonify(
            {
                "fromCurrencyCode": from_code,
                "toCurrencyCode": to_code,
                "exchangeRate": str(rate_from_inr),
            }
        ), 200

    return jsonify(
        {"error": f"Exchange rate between {from_code} and {to_code} not available."}
    ), 404


def _get_rate_to_inr(code: str) -> float | None:
    """Return the rate of `code` → INR (direct or inverse)."""
    if code == "INR":
        return 1.0
    row = CurrencyRate.query.filter_by(
        currency_code_from=code, currency_code_to="INR"
    ).first()
    if row:
        return row.exchange_rate
    inv = CurrencyRate.query.filter_by(
        currency_code_from="INR", currency_code_to=code
    ).first()
    if inv:
        return round(1 / inv.exchange_rate, 6)
    return None


def _get_rate_via_inr(from_code: str, to_code: str) -> float | None:
    """Bridge conversion: from_code → INR → to_code."""
    from_to_inr = _get_rate_to_inr(from_code)
    to_to_inr = _get_rate_to_inr(to_code)
    if from_to_inr and to_to_inr:
        return round(from_to_inr / to_to_inr, 6)
    return None
