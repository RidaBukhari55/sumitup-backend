from fastapi import APIRouter, HTTPException
from database import transcripts_collection

router = APIRouter()

@router.get("/transcript")
def get_transcript(filename: str):
    transcript = transcripts_collection.find_one({"filename": filename})
    if not transcript:
        raise HTTPException(404, "Transcript not found")

    return {
        "lecture_title": filename,
        "transcript": transcript["transcript"]
    }
