from datetime import datetime
from io import BytesIO
import boto3
import uuid
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import table
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from fastapi.responses import StreamingResponse

from database import get_db
from models import User
from core.security import SECRET_KEY, ALGORITHM




router = APIRouter()
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except JWTError:
        raise HTTPException(401, "Invalid token")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(401, "User not found")

    return user


@router.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(User).all()


 #Create S3 client
s3 = boto3.client("s3", region_name="eu-west-2")

dynamodb = boto3.resource(
    "dynamodb",
    region_name="eu-west-2"
)

BUCKET_NAME = "mychoicea12"

table = dynamodb.Table("mychoicea12")

@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    image_id = str(uuid.uuid4())
    s3_key = f"uploads/{image_id}_{file.filename}"

    # Upload to S3
    s3.upload_fileobj(
        file.file,
        BUCKET_NAME,
        s3_key,
        ExtraArgs={"ContentType": file.content_type}
        )

    image_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{s3_key}"
   
    Item={
        "image_id": image_id,
        # "user_id": user_id,
        "filename": file.filename,
        "s3_key": s3_key,
        "content_type": file.content_type,
        "uploaded_at": datetime.utcnow().isoformat()
        }

    
    table.put_item(Item=Item)
    

    return {
        "image_id": image_id,
        "url": image_url
    }
#

@router.get("/images/{image_id}")
def get_image(image_id: str):
    s3_key, content_type = get_s3_key(image_id)

    obj = s3.get_object(
        Bucket=BUCKET_NAME,
        Key=s3_key
    )

    image_bytes = obj["Body"].read()

    return StreamingResponse(
        BytesIO(image_bytes),
        media_type=content_type
    )

def get_s3_key(image_id: str):
    response = table.get_item(
        Key={"image_id": image_id}
    )

    if "Item" not in response:
        raise HTTPException(404, "Image metadata not found")

    return response["Item"]["s3_key"], response["Item"]["content_type"]
