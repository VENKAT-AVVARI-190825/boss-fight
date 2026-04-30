from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from config import config_map

db = SQLAlchemy()


def create_app(config_name: str = "default") -> Flask:
    app = Flask(__name__, static_folder="../../frontend", static_url_path="")
    app.config.from_object(config_map[config_name])

    CORS(app)
    db.init_app(app)

    from app.routes.currency import currency_bp

    app.register_blueprint(currency_bp)

    @app.route("/")
    def index() -> str:
        return app.send_static_file("index.html")

    return app
