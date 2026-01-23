from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import os
import uuid
from database import videos_collection
import yt_dlp

router = APIRouter()

VIDEO_DIR = "temp/videos"
os.makedirs(VIDEO_DIR, exist_ok=True)


def normalize_youtube_url(url: str) -> str:
    url = url.strip()
    if "/shorts/" in url:
        video_id = url.split("/shorts/")[1].split("?")[0]
        url = f"https://www.youtube.com/watch?v={video_id}"
    return url


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
        youtube_url = normalize_youtube_url(youtube_url)
        temp_name = str(uuid.uuid4())
        output_template = os.path.join(VIDEO_DIR, temp_name + ".%(ext)s")

        ydl_opts = {
            "outtmpl": output_template,
            "format": "bestvideo+bestaudio/best",
            "quiet": False,
            "noplaylist": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(youtube_url, download=True)
                filename = ydl.prepare_filename(info_dict)  # ✅ real downloaded file
            print(f"✅ YouTube video downloaded to: {filename}")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"YouTube download failed: {e}")

        video_data = {
            "original_name": youtube_url,
            "filename": os.path.basename(filename),
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
        file_path = os.path.join(VIDEO_DIR, filename)

        with open(file_path, "wb") as f:
            f.write(await file.read())

        video_data = {
            "original_name": file.filename,
            "filename": filename,
            "status": "uploaded",
            "source": "file",
            "youtube_url": None
        }

    # ✅ DB INSERT
    videos_collection.insert_one(video_data)

    return JSONResponse({
        "message": "Uploaded successfully",
        "filename": video_data["filename"]
    })
