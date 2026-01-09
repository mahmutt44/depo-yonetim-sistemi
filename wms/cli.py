from __future__ import annotations

import click
from flask import Flask

from .extensions import db
from .models import (
    Category,
    Customer,
    Product,
    Shelf,
    Supplier,
    Unit,
    User,
    Warehouse,
)


def register_cli(app: Flask) -> None:
    @app.cli.command("seed")
    def seed_command() -> None:
        """Seed data for local development."""
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            admin = User(username="admin", role=User.Role.ADMIN)
            admin.set_password("admin123")
            db.session.add(admin)

        staff = User.query.filter_by(username="personel").first()
        if not staff:
            staff = User(username="personel", role=User.Role.STAFF)
            staff.set_password("personel123")
            db.session.add(staff)

        cat = Category.query.filter_by(name="Genel").first()
        if not cat:
            cat = Category(name="Genel")
            db.session.add(cat)

        u_pcs = Unit.query.filter_by(short_code="pcs").first()
        if not u_pcs:
            u_pcs = Unit(name="Adet", short_code="pcs", is_active=True)
            db.session.add(u_pcs)

        u_kg = Unit.query.filter_by(short_code="kg").first()
        if not u_kg:
            u_kg = Unit(name="Kg", short_code="kg", is_active=True)
            db.session.add(u_kg)

        u_box = Unit.query.filter_by(short_code="box").first()
        if not u_box:
            u_box = Unit(name="Koli", short_code="box", is_active=True)
            db.session.add(u_box)

        wh1 = Warehouse.query.filter_by(name="Ana Depo").first()
        if not wh1:
            wh1 = Warehouse(name="Ana Depo", is_active=True)
            db.session.add(wh1)

        wh2 = Warehouse.query.filter_by(name="Sevkiyat Deposu").first()
        if not wh2:
            wh2 = Warehouse(name="Sevkiyat Deposu", is_active=True)
            db.session.add(wh2)

        db.session.flush()

        shelf_a1 = Shelf.query.filter_by(warehouse_id=wh1.id, code="A1").first()
        if not shelf_a1:
            shelf_a1 = Shelf(warehouse_id=wh1.id, code="A1", description="Ana Depo / A1")
            db.session.add(shelf_a1)

        shelf_b2 = Shelf.query.filter_by(warehouse_id=wh1.id, code="B2").first()
        if not shelf_b2:
            shelf_b2 = Shelf(warehouse_id=wh1.id, code="B2", description="Ana Depo / B2")
            db.session.add(shelf_b2)

        shelf_r01 = Shelf.query.filter_by(warehouse_id=wh2.id, code="R-01").first()
        if not shelf_r01:
            shelf_r01 = Shelf(warehouse_id=wh2.id, code="R-01", description="Sevkiyat / R-01")
            db.session.add(shelf_r01)

        p = Product.query.filter_by(sku="SKU-001").first()
        if not p:
            p = Product(
                name="Örnek Ürün",
                sku="SKU-001",
                barcode="000000000001",
                category=cat,
                unit=u_pcs,
                min_stock_level=10,
                description="Seed ürün",
                is_active=True,
            )
            db.session.add(p)

        s = Supplier.query.filter_by(name="Genel Tedarikçi").first()
        if not s:
            s = Supplier(name="Genel Tedarikçi", is_active=True)
            db.session.add(s)

        c = Customer.query.filter_by(name="Genel Müşteri").first()
        if not c:
            c = Customer(name="Genel Müşteri", is_active=True)
            db.session.add(c)

        db.session.commit()
        click.echo("Seed data created/updated. (admin/admin123, personel/personel123)")
