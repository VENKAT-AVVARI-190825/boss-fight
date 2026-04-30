import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from app import create_app, db
from app.seed import seed_database


@pytest.fixture(scope="session")
def app():
    application = create_app("testing")
    with application.app_context():
        db.create_all()
        seed_database()
        yield application
        db.drop_all()


@pytest.fixture(scope="session")
def client(app):
    return app.test_client()
