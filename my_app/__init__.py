from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from my_app.config import DB_CONFIG
import os

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    os.environ[
        "GOOGLE_APPLICATION_CREDENTIALS"
    ] = "/BE/BirdIndentifyBE/adept-parsec-386005-367f6742a5fe.json"

    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from my_app.routes import (
        users_blueprint,
        birds_blueprint,
        history_blueprint,
        prediction_blueprint,
    )

    app.register_blueprint(users_blueprint)
    app.register_blueprint(birds_blueprint)
    app.register_blueprint(history_blueprint)
    app.register_blueprint(prediction_blueprint)

    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers[
            "Access-Control-Allow-Headers"
        ] = "Origin, X-Requested-With, Content-Type, Accept, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, PUT, DELETE"
        return response

    return app
