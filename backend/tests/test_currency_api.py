"""
Test suite for Currency Exchange Rate API.
Covers positive and negative scenarios for /currency and /exchange-rate endpoints.
"""
import pytest


class TestListCurrencies:
    """GET /currency"""

    def test_returns_200(self, client):
        resp = client.get("/currency")
        assert resp.status_code == 200

    def test_returns_all_six_currencies(self, client):
        data = client.get("/currency").get_json()
        assert len(data) == 6

    def test_all_expected_codes_present(self, client):
        data = client.get("/currency").get_json()
        expected = {"INR", "USD", "CAD", "EUR", "AUD", "AED"}
        assert set(data.keys()) == expected

    def test_currency_object_has_required_fields(self, client):
        data = client.get("/currency").get_json()
        usd = data["USD"]
        assert "currencyCode" in usd
        assert "currencyName" in usd
        assert "countryName" in usd

    def test_inr_details_correct(self, client):
        data = client.get("/currency").get_json()
        inr = data["INR"]
        assert inr["currencyCode"] == "INR"
        assert inr["currencyName"] == "Indian Rupees"
        assert inr["countryName"] == "INDIA"


class TestDirectExchangeRate:
    """GET /exchange-rate/{fromCur}/{toCur} — stored pairs"""

    def test_usd_to_inr_returns_200(self, client):
        resp = client.get("/exchange-rate/USD/INR")
        assert resp.status_code == 200

    def test_usd_to_inr_rate(self, client):
        data = client.get("/exchange-rate/USD/INR").get_json()
        assert float(data["exchangeRate"]) == pytest.approx(80.08, rel=1e-4)

    def test_response_has_correct_fields(self, client):
        data = client.get("/exchange-rate/USD/INR").get_json()
        assert "fromCurrencyCode" in data
        assert "toCurrencyCode" in data
        assert "exchangeRate" in data

    def test_from_code_matches(self, client):
        data = client.get("/exchange-rate/USD/INR").get_json()
        assert data["fromCurrencyCode"] == "USD"

    def test_to_code_matches(self, client):
        data = client.get("/exchange-rate/USD/INR").get_json()
        assert data["toCurrencyCode"] == "INR"

    def test_eur_to_inr(self, client):
        data = client.get("/exchange-rate/EUR/INR").get_json()
        assert float(data["exchangeRate"]) == pytest.approx(93.14, rel=1e-4)

    def test_aud_to_inr(self, client):
        data = client.get("/exchange-rate/AUD/INR").get_json()
        assert float(data["exchangeRate"]) == pytest.approx(56.81, rel=1e-4)

    def test_aed_to_inr(self, client):
        data = client.get("/exchange-rate/AED/INR").get_json()
        assert float(data["exchangeRate"]) == pytest.approx(22.79, rel=1e-4)

    def test_usd_to_cad(self, client):
        data = client.get("/exchange-rate/USD/CAD").get_json()
        assert float(data["exchangeRate"]) == pytest.approx(1.36, rel=1e-4)


class TestInverseExchangeRate:
    """Inverse calculation: if A→B stored, B→A = 1/rate"""

    def test_inr_to_usd_inverse(self, client):
        resp = client.get("/exchange-rate/INR/USD")
        assert resp.status_code == 200
        data = resp.get_json()
        assert float(data["exchangeRate"]) == pytest.approx(1 / 80.08, rel=1e-4)

    def test_inr_to_eur_inverse(self, client):
        resp = client.get("/exchange-rate/INR/EUR")
        assert resp.status_code == 200
        data = resp.get_json()
        assert float(data["exchangeRate"]) == pytest.approx(1 / 93.14, rel=1e-4)

    def test_inr_to_cad_inverse(self, client):
        resp = client.get("/exchange-rate/INR/CAD")
        assert resp.status_code == 200
        data = resp.get_json()
        assert float(data["exchangeRate"]) == pytest.approx(1 / 61.62, rel=1e-4)

    def test_cad_to_usd_inverse(self, client):
        resp = client.get("/exchange-rate/CAD/USD")
        assert resp.status_code == 200
        data = resp.get_json()
        assert float(data["exchangeRate"]) == pytest.approx(1 / 1.36, rel=1e-4)


class TestBridgedExchangeRate:
    """Currency pairs not directly stored — bridged via INR."""

    def test_cad_to_eur_via_inr(self, client):
        resp = client.get("/exchange-rate/CAD/EUR")
        assert resp.status_code == 200
        data = resp.get_json()
        expected = round(61.62 / 93.14, 6)
        assert float(data["exchangeRate"]) == pytest.approx(expected, rel=1e-4)

    def test_aud_to_aed_via_inr(self, client):
        resp = client.get("/exchange-rate/AUD/AED")
        assert resp.status_code == 200
        data = resp.get_json()
        expected = round(56.81 / 22.79, 6)
        assert float(data["exchangeRate"]) == pytest.approx(expected, rel=1e-4)


class TestValidationErrors:
    """Negative test cases — invalid inputs."""

    def test_unsupported_from_currency_returns_400(self, client):
        resp = client.get("/exchange-rate/XYZ/INR")
        assert resp.status_code == 400

    def test_unsupported_to_currency_returns_400(self, client):
        resp = client.get("/exchange-rate/USD/GBP")
        assert resp.status_code == 400

    def test_both_unsupported_currencies_returns_400(self, client):
        resp = client.get("/exchange-rate/ABC/DEF")
        assert resp.status_code == 400

    def test_same_currency_returns_400(self, client):
        resp = client.get("/exchange-rate/USD/USD")
        assert resp.status_code == 400

    def test_error_field_present_in_400(self, client):
        data = client.get("/exchange-rate/USD/USD").get_json()
        assert "error" in data

    def test_case_insensitive_valid_currency(self, client):
        resp = client.get("/exchange-rate/usd/inr")
        assert resp.status_code == 200

    def test_lowercase_to_currency(self, client):
        resp = client.get("/exchange-rate/USD/inr")
        assert resp.status_code == 200

    def test_unknown_pair_but_valid_codes_returns_404_or_200(self, client):
        # EUR ↔ AED — bridged via INR so should succeed
        resp = client.get("/exchange-rate/EUR/AED")
        assert resp.status_code in (200, 404)
