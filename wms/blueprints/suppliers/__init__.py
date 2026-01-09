from flask import Blueprint

bp = Blueprint("suppliers", __name__, url_prefix="/admin")

from . import routes  # noqa: F401,E402
