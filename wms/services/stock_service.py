from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models import Shelf, StockLevel, StockMovement, User, Warehouse


@dataclass(frozen=True)
class StockMovementRequest:
    product_id: int
    warehouse_id: int
    shelf_id: int | None
    movement_type: str  # IN, OUT, ADJUST
    quantity: float
    reference_type: str  # purchase, sale, transfer, adjustment
    reason: str | None
    note: str | None
    created_by: int


class StockError(ValueError):
    pass


def _normalize_shelf_id(warehouse_id: int, shelf_id: int | None) -> int | None:
    if shelf_id is None:
        return None

    shelf = Shelf.query.get(shelf_id)
    if not shelf:
        raise StockError("Raf bulunamadı.")
    if shelf.warehouse_id != warehouse_id:
        raise StockError("Seçilen raf bu depoya ait değil.")
    return shelf_id


def create_stock_movement(req: StockMovementRequest, *, manage_transaction: bool = True) -> StockMovement:
    movement_type = (req.movement_type or "").upper().strip()
    reference_type = (req.reference_type or "").lower().strip()

    if movement_type not in {"IN", "OUT", "ADJUST"}:
        raise StockError("Geçersiz hareket tipi.")

    if movement_type in {"IN", "OUT"}:
        if req.quantity is None or req.quantity <= 0:
            raise StockError("Miktar 0'dan büyük olmalı.")

    if movement_type == "ADJUST":
        if req.quantity is None or req.quantity < 0:
            raise StockError("Hedef stok 0 veya daha büyük olmalı.")
        if not (req.reason or "").strip():
            raise StockError("ADJUST işleminde sebep (reason) zorunludur.")

    shelf_id = _normalize_shelf_id(req.warehouse_id, req.shelf_id)

    wh = Warehouse.query.get(req.warehouse_id)
    if not wh or not wh.is_active:
        raise StockError("Depo pasif veya bulunamadı.")

    user = User.query.get(req.created_by)
    if not user:
        raise StockError("Kullanıcı bulunamadı.")
    if movement_type == "ADJUST" and not user.is_admin:
        raise StockError("ADJUST işlemi sadece admin tarafından yapılabilir.")

    delta = req.quantity
    if movement_type == "OUT":
        delta = -abs(req.quantity)
    elif movement_type == "IN":
        delta = abs(req.quantity)

    now = datetime.utcnow()

    try:
        sl = (
            StockLevel.query.filter_by(
                product_id=req.product_id,
                warehouse_id=req.warehouse_id,
                shelf_id=shelf_id,
            ).first()
        )

        if not sl:
            sl = StockLevel(
                product_id=req.product_id,
                warehouse_id=req.warehouse_id,
                shelf_id=shelf_id,
                quantity=0,
            )
            db.session.add(sl)
            db.session.flush()

        current_qty = float(sl.quantity or 0)

        if movement_type == "ADJUST":
            target_qty = float(req.quantity)
            delta = target_qty - current_qty
            new_qty = target_qty
        else:
            new_qty = current_qty + float(delta)

        if new_qty < 0:
            raise StockError("Negatif stok oluşacağı için işlem reddedildi.")

        movement_qty = float(req.quantity)
        if movement_type == "ADJUST":
            movement_qty = float(delta)
        elif movement_type in {"IN", "OUT"}:
            movement_qty = abs(float(req.quantity))

        m = StockMovement(
            product_id=req.product_id,
            warehouse_id=req.warehouse_id,
            shelf_id=shelf_id,
            movement_type=movement_type,
            quantity=movement_qty,
            reference_type=reference_type,
            reason=(req.reason.strip() if req.reason else None),
            note=req.note,
            created_by=req.created_by,
            created_at=now,
        )
        db.session.add(m)

        sl.quantity = new_qty

        if manage_transaction:
            db.session.commit()

        return m
    except StockError:
        if manage_transaction:
            db.session.rollback()
        raise
    except IntegrityError as e:
        db.session.rollback()
        raise StockError("Stok güncellenemedi (veri bütünlüğü hatası).") from e
