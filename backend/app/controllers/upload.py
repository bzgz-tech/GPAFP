from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os
import uuid
from typing import List
from app.core.config import settings

router = APIRouter()

UPLOAD_DIR = "static/uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

ALLOWED_EXTENSIONS = {
    # Images
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',
    # Documents
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt', '.ppt', '.pptx', '.csv'
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    # 1. Validate Extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="File type not allowed")

    # 2. Generate Safe Filename
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # 3. Save File (and check size potentially, though usually done by middleware or reading chunks)
    # We'll read content to save it.
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")
    
    # 4. Return URL
    # Assuming the static dir is mounted at /static
    url = f"/static/uploads/{unique_filename}"
    
    return {
        "name": file.filename,
        "url": url,
        "type": file.content_type
    }
