# Test Cases Documentation

## Framework & Setup

- **Tool**: pytest + pytest-flask
- **DB**: In-memory SQLite (`sqlite:///:memory:`) — isolated from production data
- **Fixtures** (session-scoped): `app` (Flask test app), `client` (test client)
- **Run**: `cd backend && pytest tests/ -v`

---

## Test Classes

### 1. TestListCurrencies — `GET /currency`

| # | Test Name                          | Type     | Expected |
|---|------------------------------------|----------|----------|
| 1 | test_returns_200                   | Positive | HTTP 200 |
| 2 | test_returns_all_six_currencies    | Positive | 6 items in response |
| 3 | test_all_expected_codes_present    | Positive | Keys = {INR,USD,CAD,EUR,AUD,AED} |
| 4 | test_currency_object_has_required_fields | Positive | Fields present |
| 5 | test_inr_details_correct           | Positive | Exact field values |

### 2. TestDirectExchangeRate — stored pairs

| # | Test Name                   | Type     | Expected |
|---|-----------------------------|----------|----------|
| 6 | test_usd_to_inr_returns_200 | Positive | HTTP 200 |
| 7 | test_usd_to_inr_rate        | Positive | 80.08    |
| 8 | test_response_has_correct_fields | Positive | 3 fields present |
| 9 | test_from_code_matches      | Positive | fromCurrencyCode = USD |
|10 | test_to_code_matches        | Positive | toCurrencyCode = INR   |
|11 | test_eur_to_inr             | Positive | 93.14    |
|12 | test_aud_to_inr             | Positive | 56.81    |
|13 | test_aed_to_inr             | Positive | 22.79    |
|14 | test_usd_to_cad             | Positive | 1.36     |

### 3. TestInverseExchangeRate — computed inverse

| # | Test Name              | Type     | Expected             |
|---|------------------------|----------|----------------------|
|15 | test_inr_to_usd_inverse| Positive | ≈ 1/80.08 = 0.012488 |
|16 | test_inr_to_eur_inverse| Positive | ≈ 1/93.14            |
|17 | test_inr_to_cad_inverse| Positive | ≈ 1/61.62            |
|18 | test_cad_to_usd_inverse| Positive | ≈ 1/1.36             |

### 4. TestBridgedExchangeRate — INR bridge

| # | Test Name              | Type     | Expected                              |
|---|------------------------|----------|---------------------------------------|
|19 | test_cad_to_eur_via_inr| Positive | ≈ 61.62 / 93.14                       |
|20 | test_aud_to_aed_via_inr| Positive | ≈ 56.81 / 22.79                       |

### 5. TestValidationErrors — negative scenarios

| # | Test Name                                | Type     | Expected |
|---|------------------------------------------|----------|----------|
|21 | test_unsupported_from_currency           | Negative | HTTP 400 |
|22 | test_unsupported_to_currency             | Negative | HTTP 400 |
|23 | test_both_unsupported_currencies         | Negative | HTTP 400 |
|24 | test_same_currency_returns_400           | Negative | HTTP 400 |
|25 | test_error_field_present_in_400          | Negative | "error" key in JSON |
|26 | test_case_insensitive_valid_currency     | Positive | HTTP 200 (lowercase ok) |
|27 | test_lowercase_to_currency               | Positive | HTTP 200 |
|28 | test_unknown_pair_but_valid_codes        | Positive | HTTP 200 or 404 |

---

## Running Tests

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v --tb=short
```

### Expected Output (all passing)

```
tests/test_currency_api.py::TestListCurrencies::test_returns_200 PASSED
tests/test_currency_api.py::TestListCurrencies::test_returns_all_six_currencies PASSED
...
28 passed in X.XXs
```

---

## Coverage Areas

| Area                  | Covered |
|-----------------------|---------|
| List all currencies   | Yes     |
| Direct rate lookup    | Yes     |
| Inverse rate calc     | Yes     |
| INR-bridged rate calc | Yes     |
| Invalid currency code | Yes     |
| Same currency pair    | Yes     |
| Case insensitivity    | Yes     |
| Response field schema | Yes     |
| Exact numeric values  | Yes     |
