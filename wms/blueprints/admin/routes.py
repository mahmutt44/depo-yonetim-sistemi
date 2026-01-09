from datetime import date

from flask import redirect, render_template, url_for
from flask_login import login_required
from flask_login import current_user

from ...extensions import db
from ...models import Product, StockLevel, StockMovement, Warehouse
from ...security import admin_required
from . import bp


@bp.route("/")
@login_required
def index():
    if current_user.is_admin:
        return redirect(url_for("admin.dashboard"))
    return redirect(url_for("stock.stock_list"))


@bp.route("/admin/dashboard")
@admin_required
def dashboard():
    total_products = db.session.query(Product.id).count()
    total_warehouses = db.session.query(Warehouse.id).count()

    today = date.today().isoformat()
    today_in_count = (
        db.session.query(StockMovement.id)
        .filter(db.func.date(StockMovement.created_at) == today)
        .filter(StockMovement.movement_type == "IN")
        .count()
    )
    today_out_count = (
        db.session.query(StockMovement.id)
        .filter(db.func.date(StockMovement.created_at) == today)
        .filter(StockMovement.movement_type == "OUT")
        .count()
    )

    critical_products = (
        db.session.query(Product)
        .outerjoin(StockLevel, StockLevel.product_id == Product.id)
        .group_by(Product.id)
        .having(db.func.coalesce(db.func.sum(StockLevel.quantity), 0) < Product.min_stock_level)
        .count()
    )

    return render_template(
        "admin/dashboard.html",
        total_products=total_products,
        total_warehouses=total_warehouses,
        today_in_count=today_in_count,
        today_out_count=today_out_count,
        critical_products=critical_products,
    )
