from flask import Flask
from .extensions import db, jwt, swagger
from .routes.auth import auth_bp
from .routes.transaction import txn_bp

# --------------------------------------------


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    db.init_app(app)
    jwt.init_app(app)
    swagger.init_app(app)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(txn_bp, url_prefix="/api/transactions")

    return app