from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.schemas.notification import NotificationBase

def create_notification(db: Session, notification: NotificationBase, user_id: int):
    db_notification = Notification(
        **notification.dict(),
        user_id=user_id
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

def get_user_notifications(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(Notification).filter(
        Notification.user_id == user_id
    ).offset(skip).limit(limit).all()

def mark_notification_as_read(db: Session, notification_id: int):
    db_notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()
    if db_notification:
        db_notification.is_read = True
        db.commit()
        db.refresh(db_notification)
    return db_notification