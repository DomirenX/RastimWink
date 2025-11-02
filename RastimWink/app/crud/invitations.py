from sqlalchemy.orm import Session
import secrets
import string
from datetime import datetime, timedelta
from app.models.stats import EmployeeInvitation
from app.models.user import User
from app.schemas.stats import InvitationCreate
from app.auth import get_password_hash

def generate_corporate_email(full_name: str, db: Session):
    base_name = full_name.lower().replace(' ', '.')
    corporate_email = f"{base_name}@wink.ru"

    counter = 1
    while db.query(User).filter(User.email == corporate_email).first():
        corporate_email = f"{base_name}.{counter}@wink.ru"
        counter += 1

    return corporate_email

def create_invitation(db: Session, invitation: InvitationCreate, invited_by: int):
    corporate_email = generate_corporate_email(invitation.full_name, db)
    
    token = secrets.token_urlsafe(32)
    
    db_invitation = EmployeeInvitation(
        email=invitation.email,
        corporate_email=corporate_email,
        token=token,
        invited_by=invited_by,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    
    db.add(db_invitation)
    db.commit()
    db.refresh(db_invitation)
    
    return db_invitation

def activate_invitation(db: Session, token: str, password: str):
    invitation = db.query(EmployeeInvitation).filter(
        EmployeeInvitation.token == token,
        EmployeeInvitation.is_activated == False,
        EmployeeInvitation.expires_at > datetime.utcnow()
    ).first()
    
    if not invitation:
        return None
    
    user = User(
        email=invitation.corporate_email,
        password_hash=get_password_hash(password),
        full_name=invitation.email.split('@')[0].replace('.', ' ').title(),
        role="employee",
        department_id=1
    )
    
    db.add(user)
    
    invitation.is_activated = True
    invitation.activated_at = datetime.utcnow()
    
    db.commit()
    
    return user