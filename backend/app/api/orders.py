from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Header, Query, Response, status
from sqlalchemy.orm import Session, joinedload
from app.auth.dependencies import current_user
from app.core.errors import api_error
from app.db.session import get_db
from app.models import Order, OrderItem, User
from app.schemas.orders import OrderCreate, OrderRead
from app.services.audit import audit
from app.services.orders import create_order
from app.utils.pagination import apply_pagination

router = APIRouter(prefix="/orders", tags=["Orders"])


def base_query(db: Session):
    return db.query(Order).options(joinedload(Order.customer), joinedload(Order.items).joinedload(OrderItem.product)).filter(Order.deleted_at.is_(None))


@router.get("", summary="List orders with search, sorting, and pagination")
def list_orders(
    search: str | None = None,
    sort: str = Query("created_at", pattern="^(order_number|total_amount|created_at|status)$"),
    direction: str = Query("desc", pattern="^(asc|desc)$"),
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    query = base_query(db)
    if search:
        query = query.filter(Order.order_number.ilike(f"%{search}%"))
    column = getattr(Order, sort)
    query = query.order_by(column.asc() if direction == "asc" else column.desc())
    items, total, page, page_size = apply_pagination(query, page, page_size)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED, summary="Create an order transactionally")
def create(
    payload: OrderCreate,
    response: Response,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    try:
        body, code = create_order(db, payload, user, idempotency_key)
        db.commit()
    except Exception:
        db.rollback()
        raise
    response.status_code = code
    return body


@router.get("/{order_id}", response_model=OrderRead, summary="View order details")
def get_order(order_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    order = base_query(db).filter(Order.id == order_id).first()
    if not order:
        raise api_error("ORDER_NOT_FOUND", "Order not found", 404)
    return order


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Cancel an order")
def cancel_order(order_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    order = base_query(db).filter(Order.id == order_id).first()
    if not order:
        raise api_error("ORDER_NOT_FOUND", "Order not found", 404)
    order.status = "cancelled"
    order.deleted_at = datetime.now(timezone.utc)
    for item in order.items:
        item.product.quantity += item.quantity
    audit(db, "order", order.id, "cancelled", user.id)
    db.commit()
