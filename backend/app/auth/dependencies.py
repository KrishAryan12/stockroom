from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.auth.security import decode_token
from app.core.errors import api_error
from app.db.session import get_db
from app.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    subject = decode_token(token)
    if not subject:
        raise api_error("UNAUTHORIZED", "Invalid or expired token", 401)
    user = db.query(User).filter(User.id == int(subject), User.deleted_at.is_(None)).first()
    if not user:
        raise api_error("UNAUTHORIZED", "User not found", 401)
    return user
