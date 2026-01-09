from flask import Blueprint

bp = Blueprint("warehouses", __name__, url_prefix="/admin")

from . import routes  # noqa: E402,F401
