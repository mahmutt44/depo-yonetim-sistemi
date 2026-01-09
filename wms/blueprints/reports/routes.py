from __future__ import annotations

from datetime import date, timedelta

from flask import render_template, request

from ...extensions import db
from ...models import Product, StockLevel, StockMovement
from ...security import admin_required
from . import bp


def _get_days(default_days: int = 7) -> int:
    try:
        days = int(request.args.get("days") or default_days)
    except ValueError:
        days = default_days
    return max(1, min(days, 90))


@bp.route("")
@bp.route("/")
@admin_required
def index():
    days = _get_days(7)
    start_date = (date.today() - timedelta(days=days - 1)).isoformat()

    daily = (
        db.session.query(
            db.func.date(StockMovement.created_at).label("d"),
            db.func.count(StockMovement.id).label("cnt"),
        )
        .filter(db.func.date(StockMovement.created_at) >= start_date)
        .group_by(db.func.date(StockMovement.created_at))
        .order_by(db.func.date(StockMovement.created_at).asc())
        .all()
    )

    top_in = (
        db.session.query(
            Product.name.label("name"),
            Product.sku.label("sku"),
            db.func.coalesce(db.func.sum(StockMovement.quantity), 0).label("qty"),
        )
        .join(StockMovement, StockMovement.product_id == Product.id)
        .filter(db.func.date(StockMovement.created_at) >= start_date)
        .filter(StockMovement.movement_type == "IN")
        .group_by(Product.id)
        .order_by(db.func.sum(StockMovement.quantity).desc())
        .limit(10)
        .all()
    )

    top_out = (
        db.session.query(
            Product.name.label("name"),
            Product.sku.label("sku"),
            db.func.coalesce(db.func.sum(StockMovement.quantity), 0).label("qty"),
        )
        .join(StockMovement, StockMovement.product_id == Product.id)
        .filter(db.func.date(StockMovement.created_at) >= start_date)
        .filter(StockMovement.movement_type == "OUT")
        .group_by(Product.id)
        .order_by(db.func.sum(StockMovement.quantity).desc())
        .limit(10)
        .all()
    )

    low_stock = (
        db.session.query(
            Product.id.label("id"),
            Product.name.label("name"),
            Product.sku.label("sku"),
            Product.min_stock_level.label("min_level"),
            db.func.coalesce(db.func.sum(StockLevel.quantity), 0).label("qty"),
        )
        .outerjoin(StockLevel, StockLevel.product_id == Product.id)
        .group_by(Product.id)
        .having(db.func.coalesce(db.func.sum(StockLevel.quantity), 0) < Product.min_stock_level)
        .order_by(db.func.coalesce(db.func.sum(StockLevel.quantity), 0).asc())
        .limit(50)
        .all()
    )

    return render_template(
        "reports/reports_dashboard.html",
        days=days,
        daily=daily,
        top_in=top_in,
        top_out=top_out,
        low_stock=low_stock,
    )
