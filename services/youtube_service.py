import yt_dlp
import os
import uuid

def normalize_youtube_url(url: str) -> str:
    url = url.strip()
    if "/shorts/" in url:
        video_id = url.split("/shorts/")[1].split("?")[0]
        url = f"https://www.youtube.com/watch?v={video_id}"
    return url

def download_youtube_audio(url: str, save_path: str) -> str:
    url = normalize_youtube_url(url)
    print("🔗 Normalized YouTube URL:", url)

    os.makedirs(save_path, exist_ok=True)

    unique_name = f"{uuid.uuid4()}.mp3"
    output_path = os.path.join(save_path, unique_name)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "quiet": True,
        "noplaylist": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print("❌ yt-dlp failed:", e)
        raise Exception("Failed to download YouTube audio")

    if not os.path.exists(output_path):
        raise Exception("Audio download failed")

    print(f"✅ YouTube audio downloaded: {output_path}")
    return unique_name
