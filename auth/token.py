from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import RefreshToken, User
from schemas import RefreshTokenRequest
from core.security import create_access_token

router = APIRouter()

@router.post("/refresh")
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):

    stored = db.query(RefreshToken).filter(
        RefreshToken.token == request.refresh_token
    ).first()

    if not stored:
        raise HTTPException(401, "Invalid refresh token")

    user = db.query(User).filter(User.id == stored.user_id).first()

    return {
        "access_token": create_access_token({"sub": user.username}),
        "token_type": "bearer"
    }
