# Currency Exchange Rate Monitor

A full-stack web application for monitoring and converting currency exchange rates.
Built with Flask, SQLAlchemy, Pydantic v2, and vanilla JavaScript.

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Local (without Docker)](#local-without-docker)
  - [Docker](#docker)
  - [docker-compose](#docker-compose)
- [API Reference](#api-reference)
- [Supported Currencies](#supported-currencies)
- [Running Tests](#running-tests)
- [Documentation](#documentation)

---

## Overview

The Currency Exchange Rate Monitor allows users to:

- View all supported currencies and their countries
- Select two currencies and convert between them
- Automatically compute inverse rates (e.g. INR → USD from a stored USD → INR rate)
- Compute bridged rates via INR for pairs not directly stored (e.g. CAD → EUR)

### UI Preview

| Feature | Behaviour |
|---|---|
| Currency 1 dropdown | Selecting a currency removes it from Currency 2 |
| Currency 2 dropdown | Updates dynamically based on Currency 1 selection |
| Convert button | Enabled only when both currencies are selected |
| Swap button | Reverses the selected pair |
| Result card | Displays converted amount and exchange rate with timestamp |

---

## Tech Stack

| Layer | Technology | Version |
|---|---|---|
| Backend | Python | 3.12 |
| Framework | Flask | 3.1.0 |
| ORM | SQLAlchemy (Flask-SQLAlchemy) | 2.0.36 |
| Validation | Pydantic v2 | 2.10.4 |
| Database | SQLite | built-in |
| CORS | Flask-Cors | 5.0.0 |
| Testing | pytest + pytest-flask | 8.3.4 |
| Server | gunicorn | 23.0.0 |
| Container | Docker + docker-compose | — |
| Frontend | HTML5 / CSS3 / Vanilla JS (ES6) | — |

---

## Project Structure

```
boss-fight/
├── CLAUDE.md                        # AI assistant guidance and coding standards
├── README.md                        # This file
├── Dockerfile                       # Container build (python:3.12-slim)
├── docker-compose.yml               # Single-service compose (port 5000)
│
├── backend/
│   ├── run.py                       # Entry point
│   ├── config.py                    # App config, allowed currencies
│   ├── requirements.txt             # Pinned dependencies
│   └── app/
│       ├── __init__.py              # App factory + blueprint registration
│       ├── models.py                # Currency, CurrencyRate ORM models
│       ├── schemas.py               # Pydantic v2 validation schemas
│       ├── seed.py                  # Idempotent database seeder
│       └── routes/
│           └── currency.py          # GET /currency, GET /exchange-rate/{from}/{to}
│
├── backend/migrations/
│   ├── 01_create_tables.sql         # DDL scripts
│   └── 02_seed_data.sql             # Seed data inserts
│
├── backend/tests/
│   ├── conftest.py                  # pytest fixtures (in-memory SQLite)
│   └── test_currency_api.py         # 28 test cases
│
├── frontend/
│   ├── index.html                   # Single-page UI
│   ├── styles.css                   # Responsive styles
│   └── app.js                       # Fetch, dropdown logic, swap
│
└── docs/
    ├── CLAUDE_PROMPTS.txt           # All Claude commands and prompts log
    ├── CODE_LOGIC.md                # Architecture and algorithm notes
    ├── CODE_REVIEW.md               # Code review checklist
    ├── TEST_CASES.md                # Test case documentation
    ├── PROJECT_NOTE.md              # Case study rationale and design decisions
    └── MLCV-2026-6695-ClaudeE2ECaseStudy.pdf  # Original problem statement
```

---

## Getting Started

### Local (without Docker)

**Prerequisites:** Python 3.12+

```bash
# 1. Clone the repo
git clone https://github.com/VENKAT-AVVARI-190825/boss-fight.git
cd boss-fight

# 2. Install dependencies
cd backend
pip install -r requirements.txt

# 3. Start the server (creates DB and seeds data automatically)
python run.py
```

Open **http://localhost:5000** in your browser.

---

### Docker

**Prerequisites:** Docker Desktop

```bash
docker build -t currency-exchange-app .
docker run -d --name currency_exchange_app -p 5000:5000 currency-exchange-app
```

Open **http://localhost:5000** in your browser.

To stop:
```bash
docker stop currency_exchange_app && docker rm currency_exchange_app
```

---

### docker-compose

```bash
docker-compose up --build
```

---

## API Reference

### GET `/currency`

Returns all supported currencies keyed by currency code.

**Response `200`**
```json
{
  "USD": { "currencyCode": "USD", "currencyName": "US Dollars", "countryName": "USA" },
  "INR": { "currencyCode": "INR", "currencyName": "Indian Rupees", "countryName": "INDIA" }
}
```

---

### GET `/exchange-rate/{fromCur}/{toCur}`

Returns the exchange rate between two currencies.

**Path parameters**
| Parameter | Description |
|---|---|
| `fromCur` | Source currency code (case-insensitive) |
| `toCur` | Target currency code (case-insensitive) |

**Response `200`**
```json
{
  "fromCurrencyCode": "USD",
  "toCurrencyCode": "INR",
  "exchangeRate": "80.08"
}
```

**Response `400`** — unsupported currency or same currency pair
```json
{
  "error": "Currency 'XYZ' is not supported. Allowed: AED, AUD, CAD, EUR, INR, USD"
}
```

**Response `404`** — valid currencies but rate unavailable
```json
{
  "error": "Exchange rate between X and Y not available."
}
```

**Rate resolution logic (three-tier):**

| Tier | Condition | Computation |
|---|---|---|
| Direct | Pair stored in DB | Return stored rate |
| Inverse | Reverse pair stored | `1 / stored_rate` |
| INR Bridge | Neither found | `rate_from_INR / rate_to_INR` |

---

## Supported Currencies

| Code | Currency | Country |
|---|---|---|
| INR | Indian Rupees | India |
| USD | US Dollars | USA |
| CAD | Canadian Dollars | Canada |
| EUR | European Dollars | Europe |
| AUD | Australian Dollars | Australia |
| AED | UAE Dirham | UAE |

---

## Running Tests

```bash
cd backend
pytest tests/ -v
```

**Expected output:** 28 passed

| Test Class | Cases | What it covers |
|---|---|---|
| `TestListCurrencies` | 5 | GET /currency response shape and values |
| `TestDirectExchangeRate` | 9 | All 6 stored rates, response fields |
| `TestInverseExchangeRate` | 4 | Computed inverse rates (1/rate) |
| `TestBridgedExchangeRate` | 2 | INR-bridged pairs (CAD→EUR, AUD→AED) |
| `TestValidationErrors` | 8 | Invalid codes, same currency, case insensitivity |

---

## Documentation

| File | Description |
|---|---|
| [CLAUDE.md](CLAUDE.md) | Coding standards, architecture rules, and project guidance |
| [docs/CODE_REVIEW.md](docs/CODE_REVIEW.md) | Code review checklist (10 sections, 50+ checks) |
| [docs/CODE_LOGIC.md](docs/CODE_LOGIC.md) | Architecture decisions and SQL optimisation notes |
| [docs/TEST_CASES.md](docs/TEST_CASES.md) | Full test case table with expected results |
| [docs/PROJECT_NOTE.md](docs/PROJECT_NOTE.md) | Case study rationale, framework choice, prompt strategy |
| [docs/CLAUDE_PROMPTS.txt](docs/CLAUDE_PROMPTS.txt) | All Claude commands and prompts used during development |
