from sqlalchemy.orm import Session
from api import models
from api.auth import schemas, utils

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = utils.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        is_active=user.is_active,
        is_admin=user.is_admin,
        is_owner=user.is_owner,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user