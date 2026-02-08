from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import RegisterRequest
from core.security import create_access_token

router = APIRouter()

@router.post("/create-user")
def create_user(user: RegisterRequest, db: Session = Depends(get_db)):

    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(400, "Username exists")

    db_user = User(
        username=user.username,
        email=user.email,
        password=user.password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    token = create_access_token({"sub": user.username})

    return {
        "message": "User created",
        "access_token": token,
        "token_type": "bearer"
    }
