# Code Logic Documentation

## Architecture Overview

```
boss-fight/
├── backend/
│   ├── app/
│   │   ├── __init__.py       # Flask app factory, SQLAlchemy init, CORS, blueprint registration
│   │   ├── models.py         # SQLAlchemy ORM: Currency, CurrencyRate
│   │   ├── schemas.py        # Pydantic v2 validation schemas
│   │   ├── seed.py           # DB seeding logic (idempotent)
│   │   └── routes/
│   │       └── currency.py   # Blueprint: /currency, /exchange-rate
│   ├── migrations/
│   │   ├── 01_create_tables.sql
│   │   └── 02_seed_data.sql
│   ├── tests/
│   │   ├── conftest.py
│   │   └── test_currency_api.py
│   ├── config.py             # Config, TestingConfig
│   ├── run.py                # Entry point — creates tables, seeds, starts Flask
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── Dockerfile
├── docker-compose.yml
└── docs/
```

---

## Backend

### App Factory (`app/__init__.py`)

Uses the **factory pattern** (`create_app`) so the app can be instantiated
with different configs (default vs. testing). This keeps tests isolated.

- `Flask-CORS` is applied globally to allow the frontend to call the API.
- The static folder is set to `../../frontend` so `GET /` serves `index.html`.

### Models (`app/models.py`)

**Currency**
| Column        | Type    | Notes              |
|---------------|---------|--------------------|
| id            | Integer | PK, autoincrement  |
| currency_code | String  | Unique, not null   |
| currency_name | String  | Not null           |
| country_name  | String  | Not null           |

**CurrencyRate**
| Column              | Type    | Notes                        |
|---------------------|---------|------------------------------|
| id                  | Integer | PK                           |
| currency_code_from  | String  | FK → currency.currency_code  |
| currency_code_to    | String  | FK → currency.currency_code  |
| exchange_rate       | Float   | Not null                     |
| (unique constraint) |         | (from, to) pair is unique    |

### Validation (`app/schemas.py`)

Uses **Pydantic v2** `@field_validator` decorators:
- Both `from_currency` and `to_currency` are uppercased and checked against
  `ALLOWED_CURRENCIES = {"INR", "USD", "CAD", "EUR", "AUD", "AED"}`.
- `to_currency` additionally checks it differs from `from_currency`.
- Validation runs before the DB is queried — invalid input returns 400 immediately.

### Exchange Rate Logic (`app/routes/currency.py`)

Three-tier lookup for any currency pair:

```
1. Direct lookup:
   SELECT * FROM currency_rate WHERE from=A AND to=B

2. Inverse lookup (if direct not found):
   SELECT * FROM currency_rate WHERE from=B AND to=A
   → rate = 1 / stored_rate

3. INR bridge (if neither direct nor inverse found):
   rate_A_to_INR = direct or inverse of (A→INR)
   rate_B_to_INR = direct or inverse of (B→INR)
   → rate = rate_A_to_INR / rate_B_to_INR
```

This means only 6 seed rates cover all 30 possible pairs among the 6 currencies.

---

## Frontend

### Dropdown Filtering (`app.js → refreshCurrency2`)

When the user selects Currency 1:
1. `sel2` is rebuilt from `currencyMap` **excluding** the selected Currency 1 code.
2. If Currency 2 had a value that's still valid (not equal to Currency 1), it's restored.
3. The Convert button is enabled only when both selects have non-empty values.

### Conversion Flow

1. User clicks **Convert** (or presses Enter in amount field).
2. `fetch('/exchange-rate/{from}/{to}')` is called.
3. On success: `convertedAmount = amount × rate`, result card updates.
4. On error: `errorMsg` shows the API error message; result card resets.

### Swap Button

Reads both current values → sets `sel1.value = old sel2` → calls
`refreshCurrency2()` → sets `sel2.value = old sel1`. Result is cleared so
the user must re-convert after swapping.

---

## Configuration

| Setting               | Default (dev)                | Testing          |
|-----------------------|------------------------------|------------------|
| DATABASE_URL          | sqlite:///backend/currency.db| sqlite:///:memory:|
| SQLALCHEMY_TRACK_MODIFICATIONS | False            | False            |
| TESTING               | False                        | True             |

---

## SQL Query Optimisation

- `Currency.query.filter(Currency.currency_code.in_(ALLOWED_CURRENCIES))` uses
  an indexed `IN` clause on the unique `currency_code` column.
- `CurrencyRate.query.filter_by(...)` uses equality on two indexed columns
  (covered by the unique constraint index).
- Seeding uses `INSERT OR IGNORE` / existence checks to avoid duplicate inserts
  and unnecessary writes.
