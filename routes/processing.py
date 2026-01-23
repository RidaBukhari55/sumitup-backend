from fastapi import APIRouter, HTTPException
from database import videos_collection, transcripts_collection
from services.ffmpeg_service import convert_video_to_audio
from services.whisper_service import transcribe_audio
import os
from multiprocessing import Process

router = APIRouter()

VIDEO_DIR = "temp/videos"
AUDIO_DIR = "temp/audio"
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

# Tracks running processes
process_registry = {}

# ------------------------
# Background video processing
# ------------------------
def process_video_bg(video_filename: str):
    try:
        video = videos_collection.find_one({"filename": video_filename})
        if not video:
            print(f"❌ Video not found: {video_filename}")
            return

        # Stop if canceled before starting
        if video.get("status") == "canceled":
            print(f"⏹ Processing canceled: {video_filename}")
            return

        video_path = os.path.join(VIDEO_DIR, video_filename)
        audio_path = os.path.join(AUDIO_DIR, f"{os.path.splitext(video_filename)[0]}.wav")

        # Step 1: Convert video to audio
        convert_video_to_audio(video_path, audio_path)
        print(f"🎵 Audio extracted: {audio_path}")

        # Stop if canceled after audio conversion
        video = videos_collection.find_one({"filename": video_filename})
        if video.get("status") == "canceled":
            print(f"⏹ Processing canceled after audio: {video_filename}")
            return

        # Step 2: Transcribe audio
        segments = transcribe_audio(audio_path)
        if not segments:
            videos_collection.update_one({"filename": video_filename}, {"$set": {"status": "failed"}})
            print(f"❌ Transcription failed: {video_filename}")
            return

        # Step 3: Save transcript
        transcripts_collection.insert_one({
            "filename": video_filename,
            "transcript": segments
        })

        # Step 4: Mark done
        videos_collection.update_one({"filename": video_filename}, {"$set": {"status": "done"}})
        print(f"✅ Processing complete: {video_filename}")

    except Exception as e:
        print(f"❌ Processing error for {video_filename}: {e}")
        videos_collection.update_one({"filename": video_filename}, {"$set": {"status": "failed"}})
    finally:
        process_registry.pop(video_filename, None)


# ------------------------
# Start processing
# ------------------------
@router.post("/process/{video_filename}")
def process_video(video_filename: str):
    video = videos_collection.find_one({"filename": video_filename})
    if not video:
        raise HTTPException(404, "Video not found")

    if video["status"] in ["processing", "done"]:
        return {"message": "Already processing"}

    # Set status to processing immediately
    videos_collection.update_one({"filename": video_filename}, {"$set": {"status": "processing"}})

    # Start background process
    p = Process(target=process_video_bg, args=(video_filename,))
    p.start()
    process_registry[video_filename] = p

    return {"message": "Processing started"}


# ------------------------
# Cancel processing
# ------------------------
@router.post("/cancel/{video_filename}")
def cancel_processing(video_filename: str):
    # Mark as canceled
    videos_collection.update_one({"filename": video_filename}, {"$set": {"status": "canceled"}})

    # Kill process if running
    p = process_registry.get(video_filename)
    if p and p.is_alive():
        p.terminate()
        p.join()
        print(f"⏹ Background process killed: {video_filename}")

    return {"message": "Processing canceled"}


# ------------------------
# Video status
# ------------------------
@router.get("/video_status")
def get_video_status(filename: str):
    video = videos_collection.find_one({"filename": filename})
    if not video:
        return {"status": "not_found"}
    return {"status": video.get("status", "processing")}
