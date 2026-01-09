from datetime import datetime

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user

from ...extensions import db
from ...models import Product, Purchase, PurchaseItem, Shelf, Supplier, Warehouse
from ...security import admin_required
from ...services.stock_service import StockError, StockMovementRequest, create_stock_movement
from . import bp
from .forms import PurchaseForm, PurchaseItemForm


def _populate_purchase_form_choices(form: PurchaseForm) -> None:
    form.supplier_id.choices = [
        (s.id, s.name)
        for s in Supplier.query.filter_by(is_active=True).order_by(Supplier.name.asc()).all()
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


def _populate_item_form_choices(form: PurchaseItemForm) -> None:
    form.product_id.choices = [
        (p.id, f"{p.name} ({p.sku})")
        for p in Product.query.filter_by(is_active=True).order_by(Product.name.asc()).all()
    ]


@bp.route("/purchases")
@admin_required
def purchases_list():
    purchases = Purchase.query.order_by(Purchase.created_at.desc()).limit(200).all()
    return render_template("purchases/purchases_list.html", purchases=purchases)


@bp.route("/purchases/new", methods=["GET", "POST"])
@admin_required
def purchases_new():
    form = PurchaseForm()
    _populate_purchase_form_choices(form)

    if form.validate_on_submit():
        shelf_id = form.shelf_id.data if form.shelf_id.data != 0 else None

        p = Purchase(
            supplier_id=form.supplier_id.data,
            warehouse_id=form.warehouse_id.data,
            shelf_id=shelf_id,
            status=Purchase.Status.DRAFT.value,
            note=form.note.data,
            created_by=current_user.id,
        )
        db.session.add(p)
        db.session.commit()

        flash("Satın alma oluşturuldu.", "success")
        return redirect(url_for("purchases.purchases_detail", purchase_id=p.id))

    return render_template("purchases/purchase_form.html", form=form)


@bp.route("/purchases/<int:purchase_id>/edit", methods=["GET", "POST"])
@admin_required
def purchases_edit(purchase_id: int):
    p = Purchase.query.get_or_404(purchase_id)
    if p.status == Purchase.Status.RECEIVED.value:
        flash("Teslim alınmış satın alma düzenlenemez.", "warning")
        return redirect(url_for("purchases.purchases_detail", purchase_id=p.id))

    form = PurchaseForm(obj=p)
    _populate_purchase_form_choices(form)

    if form.validate_on_submit():
        p.supplier_id = form.supplier_id.data
        p.warehouse_id = form.warehouse_id.data
        p.shelf_id = form.shelf_id.data if form.shelf_id.data != 0 else None
        p.note = form.note.data
        db.session.commit()

        flash("Satın alma güncellendi.", "success")
        return redirect(url_for("purchases.purchases_detail", purchase_id=p.id))

    return render_template("purchases/purchase_form.html", form=form, purchase=p)


@bp.route("/purchases/<int:purchase_id>")
@admin_required
def purchases_detail(purchase_id: int):
    p = Purchase.query.get_or_404(purchase_id)
    items = (
        PurchaseItem.query.filter_by(purchase_id=p.id)
        .join(Product, Product.id == PurchaseItem.product_id)
        .order_by(Product.name.asc())
        .all()
    )

    item_form = PurchaseItemForm()
    _populate_item_form_choices(item_form)

    return render_template(
        "purchases/purchase_detail.html",
        purchase=p,
        items=items,
        item_form=item_form,
    )


@bp.route("/purchases/<int:purchase_id>/items/add", methods=["POST"])
@admin_required
def purchase_items_add(purchase_id: int):
    p = Purchase.query.get_or_404(purchase_id)
    if p.status == Purchase.Status.RECEIVED.value:
        flash("Teslim alınmış satın alma değiştirilemez.", "warning")
        return redirect(url_for("purchases.purchases_detail", purchase_id=p.id))

    form = PurchaseItemForm()
    _populate_item_form_choices(form)

    if form.validate_on_submit():
        if form.quantity.data is None or form.quantity.data <= 0:
            flash("Miktar 0'dan büyük olmalı.", "danger")
            return redirect(url_for("purchases.purchases_detail", purchase_id=p.id))

        existing = PurchaseItem.query.filter_by(
            purchase_id=p.id, product_id=form.product_id.data
        ).first()

        if existing:
            existing.quantity = float(existing.quantity or 0) + float(form.quantity.data)
        else:
            it = PurchaseItem(
                purchase_id=p.id,
                product_id=form.product_id.data,
                quantity=float(form.quantity.data),
            )
            db.session.add(it)

        db.session.commit()
        flash("Kalem eklendi.", "success")

    return redirect(url_for("purchases.purchases_detail", purchase_id=p.id))


@bp.route("/purchases/<int:purchase_id>/items/<int:item_id>/delete", methods=["POST"])
@admin_required
def purchase_item_delete(purchase_id: int, item_id: int):
    p = Purchase.query.get_or_404(purchase_id)
    if p.status == Purchase.Status.RECEIVED.value:
        flash("Teslim alınmış satın alma değiştirilemez.", "warning")
        return redirect(url_for("purchases.purchases_detail", purchase_id=p.id))

    it = PurchaseItem.query.filter_by(purchase_id=p.id, id=item_id).first_or_404()
    db.session.delete(it)
    db.session.commit()

    flash("Kalem silindi.", "success")
    return redirect(url_for("purchases.purchases_detail", purchase_id=p.id))


@bp.route("/purchases/<int:purchase_id>/receive", methods=["POST"])
@admin_required
def purchases_receive(purchase_id: int):
    p = Purchase.query.get_or_404(purchase_id)

    if p.status == Purchase.Status.RECEIVED.value:
        flash("Bu satın alma zaten teslim alınmış.", "warning")
        return redirect(url_for("purchases.purchases_detail", purchase_id=p.id))

    items = PurchaseItem.query.filter_by(purchase_id=p.id).all()
    if not items:
        flash("Teslim almak için en az bir kalem eklemelisiniz.", "danger")
        return redirect(url_for("purchases.purchases_detail", purchase_id=p.id))

    try:
        for it in items:
            req = StockMovementRequest(
                product_id=it.product_id,
                warehouse_id=p.warehouse_id,
                shelf_id=p.shelf_id,
                movement_type="IN",
                quantity=float(it.quantity),
                reference_type="purchase",
                reason=None,
                note=f"purchase:{p.id}",
                created_by=current_user.id,
            )
            create_stock_movement(req, manage_transaction=False)

        p.status = Purchase.Status.RECEIVED.value
        p.received_by = current_user.id
        p.received_at = datetime.utcnow()

        db.session.commit()
        flash("Satın alma teslim alındı ve stok girişleri işlendi.", "success")
    except StockError as e:
        db.session.rollback()
        flash(str(e), "danger")
    except Exception:
        db.session.rollback()
        raise

    return redirect(url_for("purchases.purchases_detail", purchase_id=p.id))
