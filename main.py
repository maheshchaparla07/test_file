from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Login API with Postgres")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#hashing of password
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    if len(password.encode("utf-8")) > 72:
        raise ValueError("Password too long (max 72 characters)")
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)



#Db connection
DATABASE_URL = "postgresql://postgres:12345678@localhost:5432/testdb"

engine = create_engine(DATABASE_URL) #bridge between the code and the database
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()


#Pydantic models and SQLAlchemy models
class RegisterRequest(BaseModel):
    id: int
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)


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

    db_user = User(
        username=user.username,
        password=hash_password(user.password),
        email=user.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"message": "User created", "id": user.id}


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
  
):
    
    print("form_data.username",form_data)
    user = db.query(User).filter(User.username == form_data.username,).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    if  not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    print("user.password",user.password)
    print(type(user.password))

    return {
        "message": "Login successful",
        "user_id": user.id,
        "username1": user.username,
    }
@app.get("/dashboard", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.id).all()
    print("User id: ",User.id)
    print(type(User.id))
    return users