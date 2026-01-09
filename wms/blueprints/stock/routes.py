from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user

from ...extensions import db
from ...models import Product, Shelf, StockLevel, StockMovement, User, Warehouse
from ...security import staff_allowed
from ...services.stock_service import StockError, StockMovementRequest, create_stock_movement
from . import bp
from .forms import StockMovementForm


@bp.route("")
@bp.route("/")
@staff_allowed
def stock_list():
    levels = (
        db.session.query(StockLevel)
        .join(Product, Product.id == StockLevel.product_id)
        .join(Warehouse, Warehouse.id == StockLevel.warehouse_id)
        .order_by(Product.name.asc(), Warehouse.name.asc())
        .all()
    )
    return render_template("stock/stock_list.html", levels=levels)


@bp.route("/movements")
@staff_allowed
def movements_list():
    movements = (
        db.session.query(StockMovement)
        .join(Product, Product.id == StockMovement.product_id)
        .join(Warehouse, Warehouse.id == StockMovement.warehouse_id)
        .outerjoin(Shelf, Shelf.id == StockMovement.shelf_id)
        .outerjoin(User, User.id == StockMovement.created_by)
        .order_by(StockMovement.created_at.desc())
        .limit(200)
        .all()
    )
    return render_template("stock/movements_list.html", movements=movements)


@bp.route("/api/shelves")
@staff_allowed
def api_shelves():
    try:
        warehouse_id = int(request.args.get("warehouse_id") or 0)
    except ValueError:
        warehouse_id = 0

    if not warehouse_id:
        return jsonify([])

    shelves = Shelf.query.filter_by(warehouse_id=warehouse_id).order_by(Shelf.code.asc()).all()
    return jsonify([{"id": s.id, "code": s.code} for s in shelves])


@bp.route("/movements/new", methods=["GET", "POST"])
@staff_allowed
def movements_new():
    form = StockMovementForm()

    if not current_user.is_admin:
        form.movement_type.choices = [("IN", "Giriş"), ("OUT", "Çıkış")]

    form.product_id.choices = [
        (p.id, f"{p.name} ({p.sku})")
        for p in Product.query.filter_by(is_active=True).order_by(Product.name.asc()).all()
    ]
    form.warehouse_id.choices = [
        (w.id, w.name)
        for w in Warehouse.query.filter_by(is_active=True).order_by(Warehouse.name.asc()).all()
    ]

    selected_wh = None
    try:
        selected_wh = int(request.form.get("warehouse_id") or form.warehouse_id.data or 0)
    except ValueError:
        selected_wh = None

    shelves = []
    if selected_wh:
        shelves = Shelf.query.filter_by(warehouse_id=selected_wh).order_by(Shelf.code.asc()).all()
    form.shelf_id.choices = [(0, "-")] + [(s.id, s.code) for s in shelves]

    if form.validate_on_submit():
        if form.movement_type.data == "ADJUST":
            if not current_user.is_admin:
                flash("ADJUST işlemi sadece admin tarafından yapılabilir.", "danger")
                return render_template("stock/movement_form.html", form=form)
            if not (form.reason.data or "").strip():
                flash("ADJUST işleminde sebep (reason) zorunludur.", "danger")
                return render_template("stock/movement_form.html", form=form)

        shelf_id = form.shelf_id.data if form.shelf_id.data != 0 else None
        req = StockMovementRequest(
            product_id=form.product_id.data,
            warehouse_id=form.warehouse_id.data,
            shelf_id=shelf_id,
            movement_type=form.movement_type.data,
            quantity=form.quantity.data,
            reference_type=form.reference_type.data,
            reason=form.reason.data,
            note=form.note.data,
            created_by=current_user.id,
        )

        try:
            create_stock_movement(req)
        except StockError as e:
            flash(str(e), "danger")
            return render_template("stock/movement_form.html", form=form)

        flash("Stok hareketi kaydedildi.", "success")
        return redirect(url_for("stock.stock_list"))

    return render_template("stock/movement_form.html", form=form)
