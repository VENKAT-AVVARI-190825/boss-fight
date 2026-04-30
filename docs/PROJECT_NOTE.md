# Project Note — Currency Exchange Rate Monitor

## 1. Reasons Behind the Choice of Case Study

The **Currency Exchange Rate Monitor** was selected as the case study for the following reasons:

### 1.1 Real-World Relevance
Currency conversion is a universally understood problem. Every user instinctively
knows what "1 USD = 80.08 INR" means, which makes it easy to verify correctness
at a glance — both during development and during evaluation. There is no ambiguity
about expected output.

### 1.2 Full-Stack Coverage in a Contained Scope
The problem naturally exercises every layer of a modern web application:
- **Database** — relational schema design, seed data, FK constraints
- **Backend API** — RESTful endpoints, input validation, business logic
- **Frontend UI** — dynamic dropdowns, fetch calls, real-time result display
- **Testing** — positive, negative, and edge-case scenarios
- **DevOps** — containerisation with Docker

This makes it an ideal case study to demonstrate end-to-end capability without
inflating scope.

### 1.3 Non-Trivial Business Logic
The exchange rate calculation is deceptively simple on the surface but requires
thoughtful design under the hood. The seed data only stores 6 directional pairs,
yet the application must resolve all 30 possible pairs among 6 currencies. This
demanded a three-tier lookup strategy (direct → inverse → INR bridge), which
demonstrates algorithmic thinking beyond basic CRUD.

### 1.4 Validation as a First-Class Concern
The requirement to restrict conversions to a fixed whitelist of currencies and
reject same-currency pairs provides a concrete validation challenge. This is
representative of real production APIs where input sanitisation is critical —
and it maps directly to Pydantic v2's `@field_validator` pattern.

### 1.5 Demonstrates Inverse Calculation Without Extra Storage
The requirement "if USD → INR is stored, INR → USD must be calculated as the
inverse in code" is a deliberate design constraint. It avoids data redundancy
while still serving bidirectional queries — a pragmatic trade-off seen in
production financial systems where rate tables can be large.

### 1.6 Testability
The deterministic nature of exchange rate arithmetic (fixed seed values, known
inverses, computable bridges) makes it straightforward to write precise test
assertions using `pytest.approx()`. This allows 28 test cases to achieve high
confidence without mocking or flaky assertions.

---

## 2. Choice of Framework

**Flask + SQLAlchemy + Pydantic** was chosen because:

- **Flask** is lightweight and unopinionated, making it ideal for a focused
  RESTful API with minimal boilerplate. Its blueprint system keeps routes modular.
- **SQLAlchemy** provides a Pythonic ORM over SQLite, with clean model
  definitions and optimised query generation (indexed lookups, `IN` clauses).
- **Pydantic v2** handles request validation and serialisation with minimal code.
  Its `@field_validator` decorators enforce the allowed-currency whitelist and
  same-currency check before any database query runs.
- **SQLite** was chosen for zero-configuration local development. The
  `DATABASE_URL` env var makes it trivial to swap in PostgreSQL for production.
- **Docker** wraps the whole stack for reproducible, one-command deployment.

**Trade-off**: Flask's synchronous model is sufficient for this use case. For
high-concurrency production needs, the app could be migrated to FastAPI + asyncio
with minimal changes to the business logic layer.

---

## 3. How Prompts Drove End-to-End Functionality

| Stage              | Prompt Focus                                        | Output |
|--------------------|-----------------------------------------------------|--------|
| Scaffolding        | Directory layout, tech stack selection              | Project structure |
| Database           | Table schema + seed data from PDF spec              | models.py, migrations/ |
| API — list         | GET /currency response shape from spec              | /currency endpoint |
| API — exchange     | Three-tier lookup (direct, inverse, bridge)         | /exchange-rate endpoint |
| Validation         | Whitelist enforcement, same-currency guard          | schemas.py (Pydantic) |
| UI                 | Dropdown filtering, amount conversion, swap         | index.html, styles.css, app.js |
| Tests              | 28 cases across 5 classes: positive + negative      | test_currency_api.py |
| Docker             | Single-command reproducible deployment              | Dockerfile, docker-compose.yml |
| Documentation      | Code logic, test cases, prompts log, project note   | docs/ |

Each prompt fed directly into a concrete deliverable — no stub code or
placeholder implementations.

---

## 4. Exchange Rate Calculation Logic

The seed data only stores 6 directional pairs. The three-tier lookup ensures
all 30 possible pairs among 6 currencies are reachable:

```
Direct:   USD → INR  →  80.08  (stored)
Inverse:  INR → USD  →  1 / 80.08  ≈ 0.012488
Bridge:   CAD → EUR  →  CAD→INR / EUR→INR  =  61.62 / 93.14  ≈ 0.6616
```

---

## 5. Unit Test Coverage

- **28 test cases** across 5 classes.
- **Positive tests**: all 6 seed rates, 4 inverse rates, 2 bridged rates,
  case-insensitive input.
- **Negative tests**: unsupported currency codes, same-currency pair, combined
  invalid codes.
- Tests run on an **in-memory SQLite** instance — no disk I/O, full isolation.

---

## 6. Additional Notes

- The Flask app serves the frontend directly from its `static_folder`, so no
  separate web server (nginx, etc.) is needed for development.
- The `seed_database()` function is **idempotent** — safe to run on every
  startup without creating duplicate rows.
- The `ALLOWED_CURRENCIES` set is defined in one place (`config.py`) and
  referenced by both the route and the Pydantic schema, keeping the whitelist DRY.
- The UI Swap button lets users reverse the conversion direction without
  re-selecting currencies manually.
