-- Table: currency
CREATE TABLE IF NOT EXISTS currency (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    currency_code VARCHAR(10)  NOT NULL UNIQUE,
    currency_name VARCHAR(100) NOT NULL,
    country_name  VARCHAR(100) NOT NULL
);

-- Table: currency_rate
CREATE TABLE IF NOT EXISTS currency_rate (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    currency_code_from  VARCHAR(10) NOT NULL REFERENCES currency(currency_code),
    currency_code_to    VARCHAR(10) NOT NULL REFERENCES currency(currency_code),
    exchange_rate       REAL        NOT NULL,
    CONSTRAINT uq_currency_pair UNIQUE (currency_code_from, currency_code_to)
);
