from __future__ import annotations

from datetime import datetime
from enum import Enum

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    class Role(str, Enum):
        ADMIN = "admin"
        STAFF = "staff"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=Role.STAFF.value)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        return self.role == self.Role.ADMIN.value


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)


class Unit(db.Model):
    __tablename__ = "units"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    short_code = db.Column(db.String(20), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)


class Supplier(db.Model):
    __tablename__ = "suppliers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(50))
    email = db.Column(db.String(200))
    address = db.Column(db.Text)
    is_active = db.Column(db.Boolean, nullable=False, default=True)


class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(50))
    email = db.Column(db.String(200))
    address = db.Column(db.Text)
    is_active = db.Column(db.Boolean, nullable=False, default=True)


class Purchase(db.Model):
    __tablename__ = "purchases"

    class Status(str, Enum):
        DRAFT = "DRAFT"
        RECEIVED = "RECEIVED"

    id = db.Column(db.Integer, primary_key=True)

    supplier_id = db.Column(db.Integer, db.ForeignKey("suppliers.id"), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouses.id"), nullable=False)
    shelf_id = db.Column(db.Integer, db.ForeignKey("shelves.id"), nullable=True)

    status = db.Column(db.String(20), nullable=False, default=Status.DRAFT.value)
    note = db.Column(db.Text)

    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    received_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    received_at = db.Column(db.DateTime, nullable=True)

    supplier = db.relationship("Supplier")
    warehouse = db.relationship("Warehouse")
    shelf = db.relationship("Shelf")
    created_user = db.relationship("User", foreign_keys=[created_by])
    received_user = db.relationship("User", foreign_keys=[received_by])


class PurchaseItem(db.Model):
    __tablename__ = "purchase_items"

    id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(db.Integer, db.ForeignKey("purchases.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Float, nullable=False)

    purchase = db.relationship(
        "Purchase", backref=db.backref("items", lazy=True, cascade="all, delete-orphan")
    )
    product = db.relationship("Product")

    __table_args__ = (
        db.UniqueConstraint("purchase_id", "product_id", name="uq_purchaseitem_purchase_product"),
    )


class Warehouse(db.Model):
    __tablename__ = "warehouses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    address = db.Column(db.Text)
    is_active = db.Column(db.Boolean, nullable=False, default=True)


class Shelf(db.Model):
    __tablename__ = "shelves"

    id = db.Column(db.Integer, primary_key=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouses.id"), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)

    warehouse = db.relationship("Warehouse", backref=db.backref("shelves", lazy=True))

    __table_args__ = (
        db.UniqueConstraint("warehouse_id", "code", name="uq_shelf_warehouse_code"),
    )


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    sku = db.Column(db.String(100), unique=True, nullable=False)
    barcode = db.Column(db.String(100), unique=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))

    unit_id = db.Column(db.Integer, db.ForeignKey("units.id"), nullable=False)

    min_stock_level = db.Column(db.Float, nullable=False, default=0)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    category = db.relationship("Category", backref=db.backref("products", lazy=True))
    unit = db.relationship("Unit")


class StockLevel(db.Model):
    __tablename__ = "stock_levels"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouses.id"), nullable=False)
    shelf_id = db.Column(db.Integer, db.ForeignKey("shelves.id"), nullable=True)
    quantity = db.Column(db.Float, nullable=False, default=0)

    product = db.relationship("Product")
    warehouse = db.relationship("Warehouse")
    shelf = db.relationship("Shelf")

    __table_args__ = (
        db.UniqueConstraint(
            "product_id",
            "warehouse_id",
            "shelf_id",
            name="uq_stocklevel_product_warehouse_shelf",
        ),
    )


class StockMovement(db.Model):
    __tablename__ = "stock_movements"

    id = db.Column(db.Integer, primary_key=True)

    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouses.id"), nullable=False)
    shelf_id = db.Column(db.Integer, db.ForeignKey("shelves.id"), nullable=True)

    movement_type = db.Column(db.String(10), nullable=False)  # IN, OUT, ADJUST
    quantity = db.Column(db.Float, nullable=False)

    reference_type = db.Column(db.String(50), nullable=False)  # purchase, sale, transfer, adjustment
    reason = db.Column(db.String(200), nullable=True)
    note = db.Column(db.Text)

    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    product = db.relationship("Product")
    warehouse = db.relationship("Warehouse")
    shelf = db.relationship("Shelf")
    user = db.relationship("User", foreign_keys=[created_by])
