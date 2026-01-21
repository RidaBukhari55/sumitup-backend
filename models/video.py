# models/video.py
from pydantic import BaseModel
from typing import Optional

class Video(BaseModel):
    original_name: str
    filename: str
    status: str = "uploaded"  # uploaded, processing, done
    youtube_url: Optional[str] = None
