from flask import Blueprint

bp = Blueprint("stock", __name__, url_prefix="/stock")

from . import routes  # noqa: E402,F401
