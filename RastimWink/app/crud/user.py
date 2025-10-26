from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.auth import get_password_hash

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email). first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id). first()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email = user.email,
        password_hash = hashed_password,
        full_name = user.full_name,
        role = user.role,
        department_id = user.department_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def update_user_role(db: Session, user_id: int, new_role: str):
    db_user = get_user_by_id(db, user_id)
    if db_user:
        db_user.role = new_role
        db.commit()
        db.refresh(db_user)
    return db_user