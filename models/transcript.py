# models/transcript.py
from pydantic import BaseModel

class Transcript(BaseModel):
    video_id: str
    text: str
