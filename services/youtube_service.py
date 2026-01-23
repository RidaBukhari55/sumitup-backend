import yt_dlp
import os
import uuid

VIDEO_DIR = "temp/videos"
AUDIO_DIR = "temp/audio"
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

def normalize_youtube_url(url: str) -> str:
    url = url.strip()
    if "/shorts/" in url:
        video_id = url.split("/shorts/")[1].split("?")[0]
        url = f"https://www.youtube.com/watch?v={video_id}"
    return url

def download_youtube_video(url: str) -> str:
    """
    Downloads YouTube video to VIDEO_DIR.
    Returns generated video filename ONLY.
    """
    url = normalize_youtube_url(url)
    print("🔗 Normalized YouTube URL:", url)

    ext = "mp4"
    filename = f"{uuid.uuid4()}.{ext}"
    output_path = os.path.join(VIDEO_DIR, filename)

    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": output_path,
        "quiet": False,
        "noplaylist": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print("❌ yt-dlp failed:", e)
        raise Exception("Failed to download YouTube video")

    print(f"✅ YouTube video downloaded: {output_path}")
    return filename
