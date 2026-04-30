# CLAUDE.md — Currency Exchange Rate Monitor

Project guidance for Claude Code. Read this before making any changes.

---

## Project Overview

A full-stack Currency Exchange Rate Monitor built with Flask (backend) and vanilla
HTML/CSS/JS (frontend). It exposes REST APIs for listing currencies and computing
exchange rates (direct, inverse, and INR-bridged), backed by SQLite via SQLAlchemy.

---

## Project Structure

```
boss-fight/
├── CLAUDE.md                        # This file
├── Dockerfile                       # Container build (python:3.12-slim)
├── docker-compose.yml               # Single-service compose (port 5000)
│
├── backend/
│   ├── run.py                       # Entry point: creates tables, seeds DB, starts Flask
│   ├── config.py                    # Config + TestingConfig; ALLOWED_CURRENCIES defined here
│   ├── requirements.txt             # Pinned Python dependencies
│   │
│   ├── app/
│   │   ├── __init__.py              # App factory (create_app), SQLAlchemy + CORS init
│   │   ├── models.py                # ORM models: Currency, CurrencyRate
│   │   ├── schemas.py               # Pydantic v2 request/response schemas + validation
│   │   ├── seed.py                  # Idempotent DB seeder (safe to run on every startup)
│   │   └── routes/
│   │       └── currency.py          # Blueprint: GET /currency, GET /exchange-rate/{from}/{to}
│   │
│   ├── migrations/
│   │   ├── 01_create_tables.sql     # DDL for currency + currency_rate tables
│   │   └── 02_seed_data.sql         # INSERT OR IGNORE seed rows
│   │
│   └── tests/
│       ├── conftest.py              # Session-scoped pytest fixtures (in-memory SQLite)
│       └── test_currency_api.py     # 28 test cases across 5 classes
│
├── frontend/
│   ├── index.html                   # Single-page UI
│   ├── styles.css                   # Responsive layout (CSS variables, grid)
│   └── app.js                       # Vanilla JS IIFE: dropdowns, fetch, swap, error handling
│
├── screenshots/
│   └── *.png                                 # UI screenshots captured during local and Docker testing
│
└── docs/
    ├── CLAUDE_PROMPTS.txt                    # All Claude commands/prompts used (required deliverable)
    ├── CODE_LOGIC.md                         # Architecture + SQL optimisation notes
    ├── CODE_REVIEW.md                        # Code review checklist with custom instructions
    ├── TEST_CASES.md                         # Full test case table with expected results
    ├── PROJECT_NOTE.md                       # Case study rationale, framework choice, prompt strategy
    └── MLCV-2026-6695-ClaudeE2ECaseStudy.pdf # Original problem statement PDF
```

---

## Tech Stack

| Layer       | Technology                  | Version  | Purpose                              |
|-------------|-----------------------------|----------|--------------------------------------|
| Backend     | Python                      | 3.12     | Runtime                              |
| Framework   | Flask                       | 3.1.0    | Web framework + blueprint routing    |
| ORM         | SQLAlchemy (via Flask-SQLAlchemy) | 2.0.36 | DB models, session, query API    |
| Validation  | Pydantic v2                 | 2.10.4   | Request validation, field validators |
| Database    | SQLite                      | built-in | Dev/test storage (file or in-memory) |
| CORS        | Flask-Cors                  | 5.0.0    | Cross-origin headers                 |
| Testing     | pytest + pytest-flask       | 8.3.4    | Unit + integration tests             |
| Server      | gunicorn                    | 23.0.0   | Production WSGI server               |
| Container   | Docker + docker-compose     | latest   | Reproducible deployment              |
| Frontend    | HTML5 / CSS3 / Vanilla JS   | —        | No framework; plain ES6 IIFE         |

---

## Architecture Decisions

### App Factory Pattern
`create_app(config_name)` in `app/__init__.py` lets tests instantiate the app
with `TestingConfig` (in-memory SQLite) without touching production state.

### Three-Tier Exchange Rate Lookup
`GET /exchange-rate/{from}/{to}` resolves rates in this order:
1. **Direct** — query `currency_rate` for the exact pair
2. **Inverse** — query the reverse pair; return `1 / rate`
3. **INR bridge** — convert both currencies to INR, then divide: `rate_A_INR / rate_B_INR`

This lets 6 seed rows cover all 30 possible pairs among the 6 supported currencies.

### Single Source of Truth for ALLOWED_CURRENCIES
`ALLOWED_CURRENCIES = {"INR", "USD", "CAD", "EUR", "AUD", "AED"}` lives in
`config.py` and is imported by both `app/routes/currency.py` and `app/schemas.py`.
Never duplicate this set — update it in one place only.

### Static Frontend via Flask
Flask serves `frontend/` as its static folder, so `GET /` returns `index.html`.
No separate web server is needed in development or Docker.

---

## Coding Standards

### Python

- **Style**: PEP 8. Line length ≤ 100 characters.
- **Type hints**: Required on all function signatures.
- **Imports**: stdlib → third-party → local, each group separated by a blank line.
- **String quotes**: Double quotes for strings, single quotes only inside f-strings when needed.
- **No bare `except`**: Always catch a specific exception class.
- **No mutable defaults**: Never use `[]` or `{}` as default argument values.
- **Validation first**: Use Pydantic schemas to validate all route inputs before touching the DB.
- **Return types**: Route functions must return a `(jsonify(...), status_code)` tuple.
- **Comments**: Only add a comment when the *why* is non-obvious. No docstrings on trivial functions.

### Flask / SQLAlchemy

- **Blueprints**: All routes live in `app/routes/`. Register blueprints in `create_app`.
- **ORM only**: Never write raw SQL in route handlers. Use SQLAlchemy query API.
- **`filter_by` vs `filter`**: Use `filter_by` for equality on known columns; `filter` for
  `IN`, comparisons, or compound conditions.
- **Session management**: Do not call `db.session.commit()` inside route handlers for reads.
  Writes (seed, future admin routes) must commit explicitly.
- **No `SELECT *` equivalent**: Always use model attributes, not `text()` queries in routes.

### Pydantic

- Use **Pydantic v2** APIs exclusively (`model_config = {...}` not inner `class Config`).
- Validators must be `@classmethod` with the `@field_validator` decorator.
- Normalise input (`.upper()`) inside validators, not in route code.

### JavaScript (Frontend)

- All frontend code is wrapped in an **IIFE** `(() => { "use strict"; ... })()`.
- No global variables. No `var` — use `const` / `let`.
- API calls use `fetch` with `async/await`.
- All DOM manipulation goes through named helper functions, not inline event handlers.
- Error states must clear previous results and display a user-readable message in `#errorMsg`.

### CSS

- Use **CSS custom properties** (`--variable-name`) for all colours, radii, and shadows.
  Never hardcode hex values outside `:root`.
- Layout uses CSS Grid for two-column converter rows; Flexbox for single-axis alignment.
- Mobile breakpoint at 560px — all multi-column layouts collapse to single column.

---

## Rules

### What to Always Do
- Run `pytest tests/ -v` after any backend change and confirm all 28 tests pass.
- Keep `ALLOWED_CURRENCIES` in sync between `config.py`, route imports, and Pydantic schema.
- Use `INSERT OR IGNORE` / existence checks in seed functions — seeding must be idempotent.
- Add `--trusted-host pypi.org --trusted-host files.pythonhosted.org` to any `pip install`
  inside the Dockerfile (corporate SSL inspection environment).
- Document any new Claude prompt used in `docs/CLAUDE_PROMPTS.txt`.
- Use `docs/CODE_REVIEW.md` as the checklist before marking any change as complete.
- Keep `docs/PROJECT_NOTE.md` updated if the case study rationale or framework decisions change.
- Refer to `docs/MLCV-2026-6695-ClaudeE2ECaseStudy.pdf` for the original requirements
  if there is any ambiguity about expected behaviour.
- Store all UI screenshots in `screenshots/` with filenames that include a visible date/timestamp.

### What to Never Do
- Do not write raw SQL strings inside route handlers or models.
- Do not add currencies outside the allowed set without updating `ALLOWED_CURRENCIES` in
  `config.py` and adding seed rows to both `seed.py` and `02_seed_data.sql`.
- Do not call `db.session.commit()` in test fixtures — use `db.drop_all()` on teardown.
- Do not import `app` directly in tests — always go through the `create_app` factory.
- Do not add a `class Config` inner class in Pydantic models — use `model_config` dict.
- Do not hardcode port numbers, database paths, or host addresses in application code —
  read them from environment variables or `config.py`.
- Do not skip the Pydantic validation layer and query the DB with unvalidated user input.

### Adding a New Currency
1. Add a row to `ALLOWED_CURRENCIES` in `config.py`.
2. Add the `Currency` row to `CURRENCIES` list in `app/seed.py`.
3. Add at least one `CurrencyRate` row (→ INR recommended for bridge coverage).
4. Append the same rows to `backend/migrations/02_seed_data.sql`.
5. Run tests — the `test_all_expected_codes_present` test will need updating.

### Adding a New API Endpoint
1. Add the route to `app/routes/currency.py` (or a new blueprint file for a new domain).
2. Create a Pydantic schema in `app/schemas.py` for any request body or path params.
3. Register a new blueprint in `app/__init__.py` if creating a new route file.
4. Write at least two positive and two negative pytest test cases.

---

## Running the Project

### Local (no Docker)
```bash
cd backend
pip install -r requirements.txt
python run.py
# visit http://localhost:5000
```

### Docker
```bash
docker build -t currency-exchange-app .
docker run -d --name currency_exchange_app -p 5000:5000 currency-exchange-app
# visit http://localhost:5000
```

### docker-compose
```bash
docker-compose up --build
```

### Tests
```bash
cd backend
pytest tests/ -v
```

---

## Environment Variables

| Variable       | Default                              | Description                  |
|----------------|--------------------------------------|------------------------------|
| `DATABASE_URL` | `sqlite:///backend/currency.db`      | SQLAlchemy connection string |

Swap in a PostgreSQL URL for production: `postgresql://user:pass@host/dbname`.
