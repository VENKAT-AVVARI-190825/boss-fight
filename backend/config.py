import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'currency.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ALLOWED_CURRENCIES = {"INR", "USD", "CAD", "EUR", "AUD", "AED"}


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


config_map = {
    "testing": TestingConfig,
    "default": Config,
}
