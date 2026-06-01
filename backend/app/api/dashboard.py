from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from fastapi import APIRouter, Depends
from app.auth.dependencies import current_user
from app.db.session import get_db
from app.models import Customer, Order, OrderItem, Product, User
from app.schemas.dashboard import DashboardRead

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardRead, summary="Return operational dashboard metrics")
def dashboard(db: Session = Depends(get_db), user: User = Depends(current_user)):
    products = db.query(Product).filter(Product.deleted_at.is_(None))
    customers = db.query(Customer).filter(Customer.deleted_at.is_(None))
    orders = db.query(Order).filter(Order.deleted_at.is_(None))
    low_stock = products.filter(Product.quantity <= Product.low_stock_threshold).order_by(Product.quantity.asc()).limit(5).all()
    inventory_value = db.query(func.coalesce(func.sum(Product.quantity * Product.unit_price), 0)).filter(Product.deleted_at.is_(None)).scalar()
    recent_orders = (
        orders.options(joinedload(Order.customer), joinedload(Order.items).joinedload(OrderItem.product))
        .order_by(Order.created_at.desc())
        .limit(6)
        .all()
    )
    return {
        "total_products": products.count(),
        "total_customers": customers.count(),
        "total_orders": orders.count(),
        "inventory_value": inventory_value,
        "low_stock_products": low_stock,
        "recent_orders": recent_orders,
        "stock_alerts": low_stock,
    }
