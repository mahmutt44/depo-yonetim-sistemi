from flask import Blueprint

bp = Blueprint("units", __name__, url_prefix="/admin")

from . import routes  # noqa: E402,F401
