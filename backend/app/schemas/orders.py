from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from app.schemas.customers import CustomerRead
from app.schemas.products import ProductRead


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    customer_id: int
    items: list[OrderItemCreate] = Field(min_length=1)


class OrderItemRead(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    line_total: Decimal
    product: ProductRead | None = None

    model_config = {"from_attributes": True}


class OrderRead(BaseModel):
    id: int
    order_number: str
    customer_id: int
    status: str
    total_amount: Decimal
    created_at: datetime
    customer: CustomerRead | None = None
    items: list[OrderItemRead] = []

    model_config = {"from_attributes": True}
