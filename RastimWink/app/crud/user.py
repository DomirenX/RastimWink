from sqlalchemy.orm import Session
from fastapi import BackgroundTasks
from app.models.user import User
from app.core.security import create_set_password_token
from app.email_service import send_set_password_email

def get_user_by_email(db: Session, email: str):
    if email is None:
        return None
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User,id == user_id).first()

def get_all_users(db: Session):
    return db.query(User).all()

def create_user_direct(db: Session, email: str, full_name: str, password_hash: str = None):
    user = User(email = email, full_name = full_name, password_hash = password_hash, is_active = bool(password_hash))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def generate_corporate_email(db: Session, first_name: str, last_name: str) -> str:
    base = f"{first_name.lower()}.{last_name.lower()}"
    domain = "@wink.ru"
    email = base + domain
    count = 1
    while db.query(User).filter(User.corporate_email == email).first():
        email = f"{base}{count}{domain}"
        count += 1
    return email

def create_user(db: Session, background_tasks: BackgroundTasks, first_name: str, last_name: str, personal_email: str):
    corporate_email = generate_corporate_email(db, first_name, last_name)
    user = User(first_name = first_name, last_name = last_name, email = personal_email, corporate_email = corporate_email, is_active = False)
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_set_password_token(user.id)
    link = f"https://wink.ru/set-password?token={token}"
    background_tasks.add_task(send_set_password_email, personal_email, corporate_email, link)
    return user