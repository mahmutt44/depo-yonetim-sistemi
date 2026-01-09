from flask import Blueprint

bp = Blueprint("purchases", __name__, url_prefix="/admin")

from . import routes  # noqa: F401,E402
