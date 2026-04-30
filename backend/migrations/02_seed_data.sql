-- Seed: currency table
INSERT OR IGNORE INTO currency (id, currency_code, currency_name, country_name) VALUES
    (1, 'INR', 'Indian Rupees',     'INDIA'),
    (2, 'USD', 'US Dollars',        'USA'),
    (3, 'CAD', 'Canadian Dollars',  'CANADA'),
    (4, 'EUR', 'European Dollars',  'EUROPE'),
    (5, 'AUD', 'Australian Dollars','AUSTRALIA'),
    (6, 'AED', 'UAE Dirham',        'UAE');

-- Seed: currency_rate table
INSERT OR IGNORE INTO currency_rate (currency_code_from, currency_code_to, exchange_rate) VALUES
    ('USD', 'INR', 80.08),
    ('CAD', 'INR', 61.62),
    ('USD', 'CAD', 1.36),
    ('EUR', 'INR', 93.14),
    ('AUD', 'INR', 56.81),
    ('AED', 'INR', 22.79);
