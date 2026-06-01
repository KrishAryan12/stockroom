from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.auth.dependencies import current_user
from app.core.errors import api_error
from app.db.session import get_db
from app.models import Customer, User
from app.schemas.customers import CustomerCreate, CustomerRead
from app.services.audit import audit
from app.utils.pagination import apply_pagination, text_search

router = APIRouter(prefix="/customers", tags=["Customers"])


def base_query(db: Session):
    return db.query(Customer).filter(Customer.deleted_at.is_(None))


@router.get("", summary="List customers with search, sorting, and pagination")
def list_customers(
    search: str | None = None,
    sort: str = Query("created_at", pattern="^(name|email|created_at)$"),
    direction: str = Query("desc", pattern="^(asc|desc)$"),
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    query = text_search(base_query(db), Customer, search, ["name", "email", "company"])
    column = getattr(Customer, sort)
    query = query.order_by(column.asc() if direction == "asc" else column.desc())
    items, total, page, page_size = apply_pagination(query, page, page_size)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.post("", response_model=CustomerRead, status_code=status.HTTP_201_CREATED, summary="Create a customer")
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    customer = Customer(**payload.model_dump())
    db.add(customer)
    try:
        db.flush()
        audit(db, "customer", customer.id, "created", user.id)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise api_error("EMAIL_EXISTS", "A customer with this email already exists", 409)
    db.refresh(customer)
    return customer


@router.get("/{customer_id}", response_model=CustomerRead, summary="View customer details")
def get_customer(customer_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    customer = base_query(db).filter(Customer.id == customer_id).first()
    if not customer:
        raise api_error("CUSTOMER_NOT_FOUND", "Customer not found", 404)
    return customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Soft delete a customer")
def delete_customer(customer_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    customer = base_query(db).filter(Customer.id == customer_id).first()
    if not customer:
        raise api_error("CUSTOMER_NOT_FOUND", "Customer not found", 404)
    customer.deleted_at = datetime.now(timezone.utc)
    audit(db, "customer", customer.id, "deleted", user.id)
    db.commit()
