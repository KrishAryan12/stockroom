from decimal import Decimal
from pydantic import BaseModel
from app.schemas.orders import OrderRead
from app.schemas.products import ProductRead


class DashboardRead(BaseModel):
    total_products: int
    total_customers: int
    total_orders: int
    revenue: Decimal
    inventory_value: Decimal
    low_stock_products: list[ProductRead]
    recent_orders: list[OrderRead]
    stock_alerts: list[ProductRead]
