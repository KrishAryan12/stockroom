from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db.session import get_db

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Application health check")
def health():
    return {"status": "ok"}


@router.get("/health/database", summary="Database health check")
def database_health(db: Session = Depends(get_db)):
    db.execute(text("select 1"))
    return {"status": "ok"}
