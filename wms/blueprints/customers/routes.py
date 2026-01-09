from flask import flash, redirect, render_template, url_for

from ...extensions import db
from ...models import Customer
from ...security import admin_required
from . import bp
from .forms import CustomerForm


@bp.route("/customers")
@admin_required
def customers_list():
    customers = Customer.query.order_by(Customer.name.asc()).all()
    return render_template("customers/customers_list.html", customers=customers)


@bp.route("/customers/new", methods=["GET", "POST"])
@admin_required
def customers_new():
    form = CustomerForm()

    if form.validate_on_submit():
        name = form.name.data.strip()

        if Customer.query.filter(db.func.lower(Customer.name) == name.lower()).first():
            flash("Bu müşteri adı zaten mevcut.", "warning")
            return render_template("customers/customer_form.html", form=form)

        c = Customer(
            name=name,
            phone=(form.phone.data or "").strip() or None,
            email=(form.email.data or "").strip() or None,
            address=form.address.data,
            is_active=bool(form.is_active.data),
        )
        db.session.add(c)
        db.session.commit()

        flash("Müşteri oluşturuldu.", "success")
        return redirect(url_for("customers.customers_list"))

    return render_template("customers/customer_form.html", form=form)


@bp.route("/customers/<int:customer_id>/edit", methods=["GET", "POST"])
@admin_required
def customers_edit(customer_id: int):
    c = Customer.query.get_or_404(customer_id)
    form = CustomerForm(obj=c)

    if form.validate_on_submit():
        name = form.name.data.strip()
        existing = (
            Customer.query.filter(db.func.lower(Customer.name) == name.lower())
            .filter(Customer.id != c.id)
            .first()
        )
        if existing:
            flash("Bu müşteri adı zaten mevcut.", "warning")
            return render_template("customers/customer_form.html", form=form, customer=c)

        c.name = name
        c.phone = (form.phone.data or "").strip() or None
        c.email = (form.email.data or "").strip() or None
        c.address = form.address.data
        c.is_active = bool(form.is_active.data)

        db.session.commit()
        flash("Müşteri güncellendi.", "success")
        return redirect(url_for("customers.customers_list"))

    return render_template("customers/customer_form.html", form=form, customer=c)


@bp.route("/customers/<int:customer_id>/toggle", methods=["POST"])
@admin_required
def customers_toggle(customer_id: int):
    c = Customer.query.get_or_404(customer_id)
    c.is_active = not c.is_active
    db.session.commit()
    flash("Müşteri durumu güncellendi.", "success")
    return redirect(url_for("customers.customers_list"))
