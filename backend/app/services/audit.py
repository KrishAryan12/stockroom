from sqlalchemy.orm import Session
from app.models import AuditLog


def audit(db: Session, entity_type: str, entity_id: int, action: str, user_id: int | None) -> None:
    db.add(AuditLog(entity_type=entity_type, entity_id=entity_id, action=action, user_id=user_id))
