# Code Review — Custom Instructions

Guidelines for reviewing any change made to the Currency Exchange Rate Monitor.
Work through each section top-to-bottom before approving or requesting changes.

---

## 1. Pre-Review Checklist

Before starting a review, confirm the following are true:

- [ ] `pytest tests/ -v` passes with **28/28** tests green (no skips)
- [ ] No new linting errors (`python -m py_compile backend/app/**/*.py`)
- [ ] The branch is up to date with `main`
- [ ] `docs/CLAUDE_PROMPTS.txt` has been updated with the new prompt/action

If any of these fail, send the change back before reviewing further.

---

## 2. Architecture & Structure

### 2.1 File Placement
- [ ] New route handlers live in `backend/app/routes/` — not in `run.py` or `__init__.py`
- [ ] New blueprints are registered in `create_app()` inside `app/__init__.py`
- [ ] Config values (URLs, flags, allowed sets) are in `config.py` — not hardcoded in route files
- [ ] New Pydantic schemas belong in `app/schemas.py`
- [ ] SQL DDL changes have a corresponding migration file in `backend/migrations/`

### 2.2 App Factory
- [ ] No code imports the `app` object directly — everything goes through `create_app()`
- [ ] Tests use the `testing` config name: `create_app("testing")`
- [ ] No application-level side effects run at import time (no DB calls outside `app_context`)

### 2.3 Currency Whitelist
- [ ] `ALLOWED_CURRENCIES` is defined only in `config.py` — not duplicated anywhere
- [ ] If a currency was added or removed, all four locations are in sync:
  - `config.py` — `ALLOWED_CURRENCIES` set
  - `app/seed.py` — `CURRENCIES` list
  - `app/seed.py` — `RATES` list (at least one rate → INR)
  - `migrations/02_seed_data.sql` — matching `INSERT OR IGNORE` rows

---

## 3. Backend — Python & Flask

### 3.1 Code Style
- [ ] PEP 8 compliant — line length ≤ 100 characters
- [ ] All function signatures have type hints on parameters and return type
- [ ] Import order: stdlib → third-party → local, each group separated by a blank line
- [ ] Double quotes used for strings; single quotes only inside f-strings
- [ ] No bare `except:` — exception type is always specified

### 3.2 Route Handlers
- [ ] Every route validates input through a Pydantic schema **before** any DB query
- [ ] All routes return a `(jsonify({...}), status_code)` tuple
- [ ] HTTP status codes are correct:
  - `200` — successful response
  - `400` — validation error (bad input, unsupported currency, same-currency pair)
  - `404` — valid inputs but rate not found
- [ ] No hardcoded port numbers, hostnames, or file paths inside route functions
- [ ] Error response always contains an `"error"` key: `{"error": "message"}`

### 3.3 SQLAlchemy
- [ ] No raw SQL strings (`text()`, `db.engine.execute()`) inside route handlers
- [ ] `filter_by()` used for simple equality; `filter()` used for `IN`, comparisons, or compound conditions
- [ ] `db.session.commit()` is **not** called inside read-only route handlers
- [ ] Queries use model attributes directly — no `SELECT *` equivalent
- [ ] FK relationships are enforced at the model level (`db.ForeignKey(...)`)

### 3.4 Pydantic Schemas
- [ ] Uses Pydantic **v2** APIs only:
  - `model_config = {...}` not inner `class Config`
  - `@field_validator` not `@validator`
  - `@classmethod` decorator present on all validators
- [ ] Input normalisation (`.upper()`, `.strip()`) happens inside validators — not in route code
- [ ] Validators raise `ValueError` with a user-readable message

### 3.5 Seeding
- [ ] `seed_database()` is idempotent — running it twice produces no duplicates and no errors
- [ ] Existence checks use `filter_by(...).first()` before inserting
- [ ] `db.session.flush()` called after Currency inserts before CurrencyRate inserts (FK dependency)

---

## 4. Backend — Tests

### 4.1 Coverage
- [ ] Every new route or code path has at least **two positive** and **two negative** test cases
- [ ] Tests cover: valid input → correct response body, invalid input → correct error + status code
- [ ] Inverse rate calculation is tested (stored A→B, queried B→A)
- [ ] Bridged rate (via INR) is tested for at least one pair

### 4.2 Test Quality
- [ ] Tests use the session-scoped `client` fixture from `conftest.py` — no direct DB calls in tests
- [ ] Numeric comparisons use `pytest.approx()` with `rel=1e-4` tolerance — no exact float equality
- [ ] No `db.session.commit()` or `db.drop_all()` calls inside individual test functions
- [ ] Test class names follow `TestFeatureName` convention
- [ ] Test function names are descriptive: `test_<what>_<expected_outcome>`

### 4.3 Isolation
- [ ] Tests do not depend on execution order
- [ ] No test writes to the production `currency.db` file
- [ ] `conftest.py` uses `sqlite:///:memory:` for the test database

---

## 5. Exchange Rate Logic

The three-tier lookup in `app/routes/currency.py` must be preserved in this order:

| Tier | Condition | Computation |
|------|-----------|-------------|
| 1 — Direct   | Row exists for `(from, to)`    | Return `exchange_rate` as-is |
| 2 — Inverse  | Row exists for `(to, from)`    | Return `round(1 / rate, 6)` |
| 3 — INR Bridge | Neither direct nor inverse found | Return `round(rate_from_INR / rate_to_INR, 6)` |

- [ ] Order of tiers has not changed
- [ ] Rounding precision is 6 decimal places for computed rates
- [ ] `_get_rate_to_inr()` handles both directions (direct and inverse to INR)
- [ ] A `404` is returned only when all three tiers fail — not before

---

## 6. Frontend

### 6.1 HTML
- [ ] Semantic HTML5 elements used (`<header>`, `<main>`, `<section>`, `<footer>`)
- [ ] All interactive elements have an associated `<label>` with matching `for`/`id`
- [ ] `aria-live="polite"` present on the result card for screen reader support
- [ ] No inline `style` attributes — all styling in `styles.css`
- [ ] No inline `onclick` or other event handlers — all wired up in `app.js`

### 6.2 JavaScript
- [ ] All code is inside the IIFE: `(() => { "use strict"; ... })()`
- [ ] No global variables — `let`/`const` only, no `var`
- [ ] All `fetch` calls use `async/await` with a `try/catch` block
- [ ] Selecting Currency 1 removes it from the Currency 2 dropdown (`refreshCurrency2()`)
- [ ] Convert button is disabled until both dropdowns have a non-empty selection
- [ ] Error messages are shown in `#errorMsg` and cleared before each new request
- [ ] Result card resets on swap, on Currency 1 change, and on API error

### 6.3 CSS
- [ ] All colour values defined as CSS custom properties in `:root` — no hardcoded hex in rules
- [ ] No `!important` declarations
- [ ] Mobile breakpoint at `560px` collapses grid to single column
- [ ] New UI elements follow the existing card pattern (`.result-card`, `.converter-card`, `.table-card`)

---

## 7. Docker

- [ ] `Dockerfile` pip install includes all three `--trusted-host` flags (corporate SSL):
  ```
  --trusted-host pypi.org
  --trusted-host pypi.python.org
  --trusted-host files.pythonhosted.org
  ```
- [ ] No secrets, `.env` files, or credentials copied into the image
- [ ] `docker-compose.yml` maps only port `5000` — no unnecessary port exposure
- [ ] Image builds successfully: `docker build -t currency-exchange-app .`
- [ ] Container starts and seeds DB on first run: `docker logs currency_exchange_app`

---

## 8. Security

- [ ] No user input is interpolated directly into SQL — all queries use SQLAlchemy ORM
- [ ] Currency codes from URL path params are validated through Pydantic before DB access
- [ ] No sensitive config (DB passwords, secret keys) hardcoded in source files
- [ ] CORS is enabled globally for development; confirm scope is appropriate for production
- [ ] No stack traces or internal paths are exposed in API error responses — only `{"error": "..."}` messages

---

## 9. Documentation

- [ ] `docs/CLAUDE_PROMPTS.txt` updated with the prompt and actions for this change
- [ ] `CLAUDE.md` updated if any architecture decision, rule, or tech stack item changed
- [ ] `docs/CODE_LOGIC.md` updated if the exchange rate algorithm or DB schema changed
- [ ] `docs/TEST_CASES.md` updated if new test cases were added or existing ones changed
- [ ] New public functions have a one-line comment only if the *why* is non-obvious

---

## 10. Final Sign-off

| Check | Result |
|-------|--------|
| All 28 pytest tests pass | Pass / Fail |
| No hardcoded config values | Pass / Fail |
| Pydantic validation in place for all inputs | Pass / Fail |
| Three-tier rate lookup order preserved | Pass / Fail |
| Frontend dropdown filtering works correctly | Pass / Fail |
| Docker builds and starts cleanly | Pass / Fail |
| CLAUDE_PROMPTS.txt updated | Pass / Fail |

A change is ready to merge only when every row above shows **Pass**.
