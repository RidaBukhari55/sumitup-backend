from fastapi import APIRouter, HTTPException
from database import videos_collection, transcripts_collection
from services.ffmpeg_service import convert_video_to_audio
from services.whisper_service import transcribe_audio
import os
from multiprocessing import Process

router = APIRouter()

VIDEO_DIR = "temp/videos"
AUDIO_DIR = "temp/audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

def process_video_bg(video_filename: str):
    try:
        video = videos_collection.find_one({"filename": video_filename})
        if not video:
            return

        # 🚨 STOP if canceled
        if video.get("status") == "canceled":
            return

        source = video.get("source")

        # =========================
        # FILE UPLOAD FLOW
        # =========================
        if source == "file":
            video_path = os.path.join(VIDEO_DIR, video_filename)
            audio_path = os.path.join(
                AUDIO_DIR, f"{os.path.splitext(video_filename)[0]}.wav"
            )

            convert_video_to_audio(video_path, audio_path)

        # =========================
        # YOUTUBE FLOW (NO FFMPEG)
        # =========================
        else:
            audio_path = os.path.join(VIDEO_DIR, video_filename)

        # 🚨 CHECK AGAIN
        video = videos_collection.find_one({"filename": video_filename})
        if video.get("status") == "canceled":
            return

        segments = transcribe_audio(audio_path)
        if not segments:
            videos_collection.update_one(
                {"filename": video_filename},
                {"$set": {"status": "failed"}}
            )
            return

        transcripts_collection.insert_one({
            "filename": video_filename,
            "transcript": segments
        })

        videos_collection.update_one(
            {"filename": video_filename},
            {"$set": {"status": "done"}}
        )

    except Exception:
        videos_collection.update_one(
            {"filename": video_filename},
            {"$set": {"status": "failed"}}
        )

@router.post("/process/{video_filename}")
def process_video(video_filename: str):
    video = videos_collection.find_one({"filename": video_filename})
    if not video:
        raise HTTPException(404, "Video not found")

    if video["status"] in ["processing", "done"]:
        return {"message": "Already processing"}

    videos_collection.update_one(
        {"filename": video_filename},
        {"$set": {"status": "processing"}}
    )

    Process(target=process_video_bg, args=(video_filename,)).start()

    return {"message": "Processing started"}

@router.post("/cancel/{video_filename}")
def cancel_processing(video_filename: str):
    videos_collection.update_one(
        {"filename": video_filename},
        {"$set": {"status": "canceled"}}
    )
    return {"message": "Processing canceled"}
