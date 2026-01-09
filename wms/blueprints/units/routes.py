from flask import flash, redirect, render_template, url_for

from ...extensions import db
from ...models import Unit
from ...security import admin_required
from . import bp
from .forms import UnitForm


@bp.route("/units")
@admin_required
def units_list():
    units = Unit.query.order_by(Unit.name.asc()).all()
    return render_template("units/units_list.html", units=units)


@bp.route("/units/new", methods=["GET", "POST"])
@admin_required
def units_new():
    form = UnitForm()
    if form.validate_on_submit():
        name = form.name.data.strip()
        short_code = form.short_code.data.strip()

        if Unit.query.filter(db.func.lower(Unit.name) == name.lower()).first():
            flash("Bu birim adı zaten mevcut.", "warning")
            return render_template("units/unit_form.html", form=form)

        if Unit.query.filter(db.func.lower(Unit.short_code) == short_code.lower()).first():
            flash("Bu kısa kod zaten mevcut.", "warning")
            return render_template("units/unit_form.html", form=form)

        u = Unit(name=name, short_code=short_code, is_active=bool(form.is_active.data))
        db.session.add(u)
        db.session.commit()

        flash("Birim oluşturuldu.", "success")
        return redirect(url_for("units.units_list"))

    return render_template("units/unit_form.html", form=form)


@bp.route("/units/<int:unit_id>/toggle", methods=["POST"])
@admin_required
def units_toggle(unit_id: int):
    u = Unit.query.get_or_404(unit_id)
    u.is_active = not u.is_active
    db.session.commit()
    flash("Birim durumu güncellendi.", "success")
    return redirect(url_for("units.units_list"))
