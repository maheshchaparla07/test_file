from email.mime import base
import token
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from fastapi.middleware.cors import CORSMiddleware

from email.mime import base
from sqlalchemy.orm import declarative_base

Base = declarative_base()




from jose import jwt, JWTError
from datetime import datetime, timedelta
import secrets

SECRET_KEY = secrets.token_hex(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 20

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

app = FastAPI(title="Login API with Postgres")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#hashing of password
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# def hash_password(password: str) -> str:
#     if len(password.encode("utf-8")) > 72:
#         raise ValueError("Password too long (max 72 characters)")
#     return pwd_context.hash(password)

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     return pwd_context.verify(plain_password, hashed_password)


#Db connection
DATABASE_URL = "postgresql://postgres:12345678@localhost:5432/testdb"

engine = create_engine(DATABASE_URL) #bridge between the code and the database
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()


#Pydantic models and SQLAlchemy models
class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str

class LoginRequest(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    email: str
    username: str
    
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str]  = None

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True,nullable=False)
    password = Column(String)

Base.metadata.create_all(bind=engine)

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    user_id = Column(Integer)
    
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/create-user")
def create_user(user:RegisterRequest, db: Session = Depends(get_db)):
    
    username_exists = db.query(User).filter(
        User.username == user.username
    ).first()

    email_exists = db.query(User).filter(
        User.email == user.email
    ).first()
    
    if username_exists or email_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="USERNAME/ERROR_EXISTS"
        )

    db_user = User(
        username=user.username,
        password=user.password,
        email=user.email
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    token = create_access_token({"sub": user.username})
    print("Generated token after registration: ", token)
    return {"message": "User created", 
            "id": db_user.id,
            "access_token": token,
            "token_type": "bearer",
            "message": "Login successful"
            }

@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()

    if (form_data.password != user.password) or (form_data.username != user.username):
        raise HTTPException(status_code=401, detail="Invalid credentialsusername or  password")
    
    access_token = create_access_token(data={"sub": user.username})

    refresh_token = create_refresh_token()


    print("Generated token after login: ", access_token)

    db_refresh = RefreshToken(
        token=refresh_token,
        user_id=user.id
    )

    db.add(db_refresh)
    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "Login successful"
    }

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = db.query(User).filter(User.username == username).first()

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.get("/dashboard", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    users = db.query(User).order_by(User.id).all()
    # if User.id == 1:
    print("User id: ",User.id)
    print(type(User.id))
    return users

@app.put("/users/{user_id}")
def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    
):
    
    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.email = user.email
    db_user.username = user.username

    db.commit()
    db.refresh(db_user)

    return {"message": "User updated successfully"}

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS)
    to_encode.update({"exp": expire})
    token= jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token



def create_refresh_token():
    return secrets.token_urlsafe(64)


@app.post("/refresh")
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):

    stored_token = db.query(RefreshToken).filter(
        RefreshToken.token == refresh_token
    ).first()

    if not stored_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = db.query(User).filter(User.id == stored_token.user_id).first()

    new_access_token = create_access_token({"sub": user.username})

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

