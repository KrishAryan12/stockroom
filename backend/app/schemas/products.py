from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    sku: str = Field(min_length=2, max_length=80)
    description: str | None = None
    unit_price: Decimal = Field(gt=0)
    quantity: int = Field(ge=0)
    low_stock_threshold: int = Field(default=5, ge=0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=180)
    sku: str | None = Field(default=None, min_length=2, max_length=80)
    description: str | None = None
    unit_price: Decimal | None = Field(default=None, gt=0)
    quantity: int | None = Field(default=None, ge=0)
    low_stock_threshold: int | None = Field(default=None, ge=0)


class ProductRead(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
