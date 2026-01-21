from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import os
import uuid
from database import videos_collection
from services.youtube_service import download_youtube_audio



router = APIRouter()

UPLOAD_DIR = "temp/videos"
os.makedirs(UPLOAD_DIR, exist_ok=True)




@router.post("/upload")
async def upload_video(
    file: UploadFile = File(None),
    youtube_url: str = Form(None)
):

    print("Received file:", file)
    print("Received youtube_url:", youtube_url)
    # 🔴 Validation
    if not file and not youtube_url:
        raise HTTPException(status_code=400, detail="File or YouTube URL required")

    # ==========================
    # ✅ CASE 1: YOUTUBE LINK
    # ==========================
    if youtube_url:
        try:
            filename = download_youtube_audio(youtube_url, UPLOAD_DIR)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

        video_data = {
            "original_name": youtube_url,
            "filename": filename,
            "status": "uploaded",
            "source": "youtube",
            "youtube_url": youtube_url
        }

    # ==========================
    # ✅ CASE 2: FILE UPLOAD
    # ==========================
    else:
        ext = file.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as f:
            f.write(await file.read())

        video_data = {
            "original_name": file.filename,
            "filename": filename,
            "status": "uploaded",
            "source": "file",
            "youtube_url": None
        }

    # ✅ DB INSERT (CRITICAL)
    videos_collection.insert_one(video_data)

    return JSONResponse({
        "message": "Uploaded successfully",
        "filename": filename
    })
