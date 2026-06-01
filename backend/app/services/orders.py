import hashlib
import json
from decimal import Decimal
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, joinedload
from app.core.errors import api_error
from app.models import Customer, IdempotencyRecord, Order, OrderItem, Product, User
from app.schemas.orders import OrderCreate, OrderRead
from app.services.audit import audit


def payload_hash(payload: OrderCreate) -> str:
    canonical = json.dumps(payload.model_dump(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def create_order(db: Session, payload: OrderCreate, user: User, idempotency_key: str | None):
    request_hash = payload_hash(payload)
    if idempotency_key:
        record = (
            db.query(IdempotencyRecord)
            .filter(IdempotencyRecord.user_id == user.id, IdempotencyRecord.key == idempotency_key)
            .first()
        )
        if record:
            if record.request_hash != request_hash:
                raise api_error("IDEMPOTENCY_CONFLICT", "This idempotency key was used with a different payload", 409)
            return json.loads(record.response_body), record.status_code

    customer = db.query(Customer).filter(Customer.id == payload.customer_id, Customer.deleted_at.is_(None)).first()
    if not customer:
        raise api_error("CUSTOMER_NOT_FOUND", "Customer not found", 404)

    product_ids = [item.product_id for item in payload.items]
    products = (
        db.query(Product)
        .filter(Product.id.in_(product_ids), Product.deleted_at.is_(None))
        .with_for_update()
        .all()
    )
    product_map = {product.id: product for product in products}
    if len(product_map) != len(set(product_ids)):
        raise api_error("PRODUCT_NOT_FOUND", "One or more products were not found", 404)

    total = Decimal("0.00")
    order = Order(customer_id=customer.id, order_number="pending", total_amount=total)
    db.add(order)
    db.flush()
    order.order_number = f"SO-{order.id:06d}"

    for item in payload.items:
        product = product_map[item.product_id]
        if product.quantity < item.quantity:
            raise api_error("INSUFFICIENT_STOCK", f"Only {product.quantity} units available for {product.name}", 409)
        product.quantity -= item.quantity
        line_total = Decimal(product.unit_price) * item.quantity
        total += line_total
        db.add(OrderItem(order_id=order.id, product_id=product.id, quantity=item.quantity, unit_price=product.unit_price, line_total=line_total))

    order.total_amount = total
    audit(db, "order", order.id, "created", user.id)
    db.flush()

    created = (
        db.query(Order)
        .options(joinedload(Order.customer), joinedload(Order.items).joinedload(OrderItem.product))
        .filter(Order.id == order.id)
        .first()
    )
    body = jsonable_encoder(OrderRead.model_validate(created), by_alias=False)

    if idempotency_key:
        db.add(
            IdempotencyRecord(
                user_id=user.id,
                key=idempotency_key,
                request_hash=request_hash,
                response_body=json.dumps(body, default=str),
                status_code=201,
            )
        )
    return body, 201
