import os

from flask import Flask
from dotenv import load_dotenv

from .config import Config
from .extensions import db, login_manager, migrate, csrf
from .cli import register_cli


def create_app(config_object: type[Config] | None = None) -> Flask:
    load_dotenv()

    app = Flask(__name__, instance_relative_config=True)

    os.makedirs(app.instance_path, exist_ok=True)

    cfg = config_object or Config
    app.config.from_object(cfg)

    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        app.config["SQLALCHEMY_DATABASE_URI"] = (
            "sqlite:///" + os.path.join(app.instance_path, "wms.sqlite3")
        )

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = app.config.get("LOGIN_VIEW", "auth.login")
    migrate.init_app(app, db)
    csrf.init_app(app)

    from .blueprints.auth import bp as auth_bp
    from .blueprints.admin import bp as admin_bp
    from .blueprints.products import bp as products_bp
    from .blueprints.units import bp as units_bp
    from .blueprints.stock import bp as stock_bp
    from .blueprints.warehouses import bp as warehouses_bp
    from .blueprints.reports import bp as reports_bp
    from .blueprints.suppliers import bp as suppliers_bp
    from .blueprints.customers import bp as customers_bp
    from .blueprints.purchases import bp as purchases_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(units_bp)
    app.register_blueprint(stock_bp)
    app.register_blueprint(warehouses_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(purchases_bp)

    register_cli(app)

    return app
