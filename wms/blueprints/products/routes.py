from flask import flash, redirect, render_template, url_for

from ...extensions import db
from ...models import Category, Product, Unit
from ...security import admin_required
from . import bp
from .forms import CategoryForm, ProductForm


@bp.route("/categories")
@admin_required
def categories_list():
    categories = Category.query.order_by(Category.name.asc()).all()
    return render_template("products/categories_list.html", categories=categories)


@bp.route("/categories/new", methods=["GET", "POST"])
@admin_required
def categories_new():
    form = CategoryForm()
    if form.validate_on_submit():
        existing = Category.query.filter_by(name=form.name.data.strip()).first()
        if existing:
            flash("Bu kategori zaten mevcut.", "warning")
            return render_template("products/category_form.html", form=form)

        c = Category(name=form.name.data.strip())
        db.session.add(c)
        db.session.commit()
        flash("Kategori oluşturuldu.", "success")
        return redirect(url_for("products.categories_list"))

    return render_template("products/category_form.html", form=form)


@bp.route("/products")
@admin_required
def products_list():
    products = Product.query.order_by(Product.name.asc()).all()
    return render_template("products/products_list.html", products=products)


@bp.route("/products/new", methods=["GET", "POST"])
@admin_required
def products_new():
    form = ProductForm()
    form.category_id.choices = [(0, "-")] + [
        (c.id, c.name) for c in Category.query.order_by(Category.name.asc()).all()
    ]
    form.unit_id.choices = [
        (u.id, f"{u.name} ({u.short_code})")
        for u in Unit.query.filter_by(is_active=True).order_by(Unit.name.asc()).all()
    ]

    if form.validate_on_submit():
        if Product.query.filter_by(sku=form.sku.data.strip()).first():
            flash("SKU zaten kullanılıyor.", "warning")
            return render_template("products/product_form.html", form=form)

        p = Product(
            name=form.name.data.strip(),
            sku=form.sku.data.strip(),
            barcode=(form.barcode.data.strip() if form.barcode.data else None),
            category_id=(form.category_id.data or None) if form.category_id.data != 0 else None,
            unit_id=form.unit_id.data,
            min_stock_level=form.min_stock_level.data or 0,
            description=form.description.data,
            is_active=bool(form.is_active.data),
        )
        db.session.add(p)
        db.session.commit()
        flash("Ürün oluşturuldu.", "success")
        return redirect(url_for("products.products_list"))

    return render_template("products/product_form.html", form=form)
