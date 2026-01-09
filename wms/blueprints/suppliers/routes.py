from flask import flash, redirect, render_template, url_for

from ...extensions import db
from ...models import Supplier
from ...security import admin_required
from . import bp
from .forms import SupplierForm


@bp.route("/suppliers")
@admin_required
def suppliers_list():
    suppliers = Supplier.query.order_by(Supplier.name.asc()).all()
    return render_template("suppliers/suppliers_list.html", suppliers=suppliers)


@bp.route("/suppliers/new", methods=["GET", "POST"])
@admin_required
def suppliers_new():
    form = SupplierForm()

    if form.validate_on_submit():
        name = form.name.data.strip()

        if Supplier.query.filter(db.func.lower(Supplier.name) == name.lower()).first():
            flash("Bu tedarikçi adı zaten mevcut.", "warning")
            return render_template("suppliers/supplier_form.html", form=form)

        s = Supplier(
            name=name,
            phone=(form.phone.data or "").strip() or None,
            email=(form.email.data or "").strip() or None,
            address=form.address.data,
            is_active=bool(form.is_active.data),
        )
        db.session.add(s)
        db.session.commit()

        flash("Tedarikçi oluşturuldu.", "success")
        return redirect(url_for("suppliers.suppliers_list"))

    return render_template("suppliers/supplier_form.html", form=form)


@bp.route("/suppliers/<int:supplier_id>/edit", methods=["GET", "POST"])
@admin_required
def suppliers_edit(supplier_id: int):
    s = Supplier.query.get_or_404(supplier_id)
    form = SupplierForm(obj=s)

    if form.validate_on_submit():
        name = form.name.data.strip()
        existing = (
            Supplier.query.filter(db.func.lower(Supplier.name) == name.lower())
            .filter(Supplier.id != s.id)
            .first()
        )
        if existing:
            flash("Bu tedarikçi adı zaten mevcut.", "warning")
            return render_template("suppliers/supplier_form.html", form=form, supplier=s)

        s.name = name
        s.phone = (form.phone.data or "").strip() or None
        s.email = (form.email.data or "").strip() or None
        s.address = form.address.data
        s.is_active = bool(form.is_active.data)

        db.session.commit()
        flash("Tedarikçi güncellendi.", "success")
        return redirect(url_for("suppliers.suppliers_list"))

    return render_template("suppliers/supplier_form.html", form=form, supplier=s)


@bp.route("/suppliers/<int:supplier_id>/toggle", methods=["POST"])
@admin_required
def suppliers_toggle(supplier_id: int):
    s = Supplier.query.get_or_404(supplier_id)
    s.is_active = not s.is_active
    db.session.commit()
    flash("Tedarikçi durumu güncellendi.", "success")
    return redirect(url_for("suppliers.suppliers_list"))
