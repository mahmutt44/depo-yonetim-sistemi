from flask import flash, redirect, render_template, url_for

from ...extensions import db
from ...models import Shelf, StockLevel, StockMovement, Warehouse
from ...security import admin_required
from . import bp
from .forms import ShelfForm, WarehouseForm


@bp.route("/warehouses")
@admin_required
def warehouses_list():
    warehouses = Warehouse.query.order_by(Warehouse.name.asc()).all()
    return render_template("warehouses/warehouses_list.html", warehouses=warehouses)


@bp.route("/warehouses/new", methods=["GET", "POST"])
@admin_required
def warehouses_new():
    form = WarehouseForm()
    if form.validate_on_submit():
        name = form.name.data.strip()
        existing = Warehouse.query.filter(db.func.lower(Warehouse.name) == name.lower()).first()
        if existing:
            flash("Bu depo adı zaten mevcut.", "warning")
            return render_template("warehouses/warehouse_form.html", form=form)

        w = Warehouse(name=name, address=form.address.data, is_active=bool(form.is_active.data))
        db.session.add(w)
        db.session.commit()

        flash("Depo oluşturuldu.", "success")
        return redirect(url_for("warehouses.warehouses_list"))

    return render_template("warehouses/warehouse_form.html", form=form)


@bp.route("/warehouses/<int:warehouse_id>/edit", methods=["GET", "POST"])
@admin_required
def warehouses_edit(warehouse_id: int):
    w = Warehouse.query.get_or_404(warehouse_id)
    form = WarehouseForm(obj=w)

    if form.validate_on_submit():
        name = form.name.data.strip()
        existing = (
            Warehouse.query.filter(db.func.lower(Warehouse.name) == name.lower())
            .filter(Warehouse.id != w.id)
            .first()
        )
        if existing:
            flash("Bu depo adı zaten mevcut.", "warning")
            return render_template("warehouses/warehouse_form.html", form=form, warehouse=w)

        w.name = name
        w.address = form.address.data
        w.is_active = bool(form.is_active.data)
        db.session.commit()

        flash("Depo güncellendi.", "success")
        return redirect(url_for("warehouses.warehouses_list"))

    return render_template("warehouses/warehouse_form.html", form=form, warehouse=w)


@bp.route("/warehouses/<int:warehouse_id>/toggle", methods=["POST"])
@admin_required
def warehouses_toggle(warehouse_id: int):
    w = Warehouse.query.get_or_404(warehouse_id)
    w.is_active = not w.is_active
    db.session.commit()
    flash("Depo durumu güncellendi.", "success")
    return redirect(url_for("warehouses.warehouses_list"))


@bp.route("/warehouses/<int:warehouse_id>/shelves")
@admin_required
def shelves_list(warehouse_id: int):
    w = Warehouse.query.get_or_404(warehouse_id)
    shelves = Shelf.query.filter_by(warehouse_id=w.id).order_by(Shelf.code.asc()).all()
    return render_template("warehouses/shelves_list.html", warehouse=w, shelves=shelves)


@bp.route("/warehouses/<int:warehouse_id>/shelves/new", methods=["GET", "POST"])
@admin_required
def shelves_new(warehouse_id: int):
    w = Warehouse.query.get_or_404(warehouse_id)
    form = ShelfForm()

    if form.validate_on_submit():
        code = form.code.data.strip()
        existing = Shelf.query.filter_by(warehouse_id=w.id, code=code).first()
        if existing:
            flash("Bu raf kodu bu depoda zaten mevcut.", "warning")
            return render_template("warehouses/shelf_form.html", form=form, warehouse=w)

        s = Shelf(warehouse_id=w.id, code=code, description=form.description.data)
        db.session.add(s)
        db.session.commit()

        flash("Raf oluşturuldu.", "success")
        return redirect(url_for("warehouses.shelves_list", warehouse_id=w.id))

    return render_template("warehouses/shelf_form.html", form=form, warehouse=w)


@bp.route("/shelves/<int:shelf_id>/edit", methods=["GET", "POST"])
@admin_required
def shelves_edit(shelf_id: int):
    s = Shelf.query.get_or_404(shelf_id)
    w = Warehouse.query.get_or_404(s.warehouse_id)
    form = ShelfForm(obj=s)

    if form.validate_on_submit():
        code = form.code.data.strip()
        existing = (
            Shelf.query.filter_by(warehouse_id=w.id, code=code)
            .filter(Shelf.id != s.id)
            .first()
        )
        if existing:
            flash("Bu raf kodu bu depoda zaten mevcut.", "warning")
            return render_template("warehouses/shelf_form.html", form=form, warehouse=w, shelf=s)

        s.code = code
        s.description = form.description.data
        db.session.commit()

        flash("Raf güncellendi.", "success")
        return redirect(url_for("warehouses.shelves_list", warehouse_id=w.id))

    return render_template("warehouses/shelf_form.html", form=form, warehouse=w, shelf=s)


@bp.route("/shelves/<int:shelf_id>/delete", methods=["POST"])
@admin_required
def shelves_delete(shelf_id: int):
    s = Shelf.query.get_or_404(shelf_id)
    w = Warehouse.query.get_or_404(s.warehouse_id)

    used_in_levels = StockLevel.query.filter_by(shelf_id=s.id).count()
    used_in_movements = StockMovement.query.filter_by(shelf_id=s.id).count()
    if used_in_levels or used_in_movements:
        flash("Bu raf stok kayıtlarında kullanıldığı için silinemez.", "danger")
        return redirect(url_for("warehouses.shelves_list", warehouse_id=w.id))

    db.session.delete(s)
    db.session.commit()
    flash("Raf silindi.", "success")
    return redirect(url_for("warehouses.shelves_list", warehouse_id=w.id))
