from fastapi import APIRouter, Depends, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.auth.dependencies import current_user
from app.auth.security import create_access_token, hash_password, verify_password
from app.core.errors import api_error
from app.db.session import get_db
from app.models import User
from app.schemas.auth import Token, UserCreate, UserLogin, UserRead

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED, summary="Register a new user")
def register(payload: UserCreate, db: Session = Depends(get_db)):
    user = User(name=payload.name, email=payload.email.lower(), password_hash=hash_password(payload.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise api_error("EMAIL_EXISTS", "A user with this email already exists", 409)
    db.refresh(user)
    return {"access_token": create_access_token(str(user.id)), "user": user}


@router.post("/login", response_model=Token, summary="Exchange credentials for a JWT")
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower(), User.deleted_at.is_(None)).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise api_error("INVALID_CREDENTIALS", "Email or password is incorrect", 401)
    return {"access_token": create_access_token(str(user.id)), "user": user}


@router.get("/me", response_model=UserRead, summary="Return the authenticated user")
def me(user: User = Depends(current_user)):
    return user
