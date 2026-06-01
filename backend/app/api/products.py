from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.auth.dependencies import current_user
from app.core.errors import api_error
from app.db.session import get_db
from app.models import Product, User
from app.schemas.products import ProductCreate, ProductRead, ProductUpdate
from app.services.audit import audit
from app.utils.pagination import apply_pagination, text_search

router = APIRouter(prefix="/products", tags=["Products"])


def base_query(db: Session):
    return db.query(Product).filter(Product.deleted_at.is_(None))


@router.get("", summary="List products with search, sorting, and pagination")
def list_products(
    search: str | None = None,
    sort: str = Query("created_at", pattern="^(name|sku|quantity|unit_price|created_at)$"),
    direction: str = Query("desc", pattern="^(asc|desc)$"),
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    query = text_search(base_query(db), Product, search, ["name", "sku"])
    column = getattr(Product, sort)
    query = query.order_by(column.asc() if direction == "asc" else column.desc())
    items, total, page, page_size = apply_pagination(query, page, page_size)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED, summary="Create a product")
def create_product(payload: ProductCreate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    product = Product(**payload.model_dump())
    db.add(product)
    try:
        db.flush()
        audit(db, "product", product.id, "created", user.id)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise api_error("SKU_EXISTS", "A product with this SKU already exists", 409)
    db.refresh(product)
    return product


@router.get("/{product_id}", response_model=ProductRead, summary="View product details")
def get_product(product_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    product = base_query(db).filter(Product.id == product_id).first()
    if not product:
        raise api_error("PRODUCT_NOT_FOUND", "Product not found", 404)
    return product


def apply_product_update(product_id: int, payload: ProductUpdate, db: Session, user: User):
    product = base_query(db).filter(Product.id == product_id).first()
    if not product:
        raise api_error("PRODUCT_NOT_FOUND", "Product not found", 404)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    try:
        audit(db, "product", product.id, "updated", user.id)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise api_error("SKU_EXISTS", "A product with this SKU already exists", 409)
    db.refresh(product)
    return product


@router.put("/{product_id}", response_model=ProductRead, summary="Update a product")
def replace_product(product_id: int, payload: ProductCreate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    return apply_product_update(product_id, ProductUpdate(**payload.model_dump()), db, user)


@router.patch("/{product_id}", response_model=ProductRead, summary="Partially update a product")
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    return apply_product_update(product_id, payload, db, user)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Soft delete a product")
def delete_product(product_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    product = base_query(db).filter(Product.id == product_id).first()
    if not product:
        raise api_error("PRODUCT_NOT_FOUND", "Product not found", 404)
    product.deleted_at = datetime.now(timezone.utc)
    audit(db, "product", product.id, "deleted", user.id)
    db.commit()
