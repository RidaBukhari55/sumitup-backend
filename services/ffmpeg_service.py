# services/ffmpeg_service.py
import ffmpeg
import os

def convert_video_to_audio(video_path, audio_path):
    try:
        print(f"🔹 Converting video: {video_path} → {audio_path}")
        (
            ffmpeg
            .input(video_path)
            .output(audio_path, ac=1, ar=16000)  # mono, 16kHz
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)  # capture output
        )
        if os.path.exists(audio_path):
            print(f"✅ Audio successfully created at {audio_path}")
        else:
            print("❌ Audio file not found after conversion")
        return audio_path
    except ffmpeg.Error as e:
        print("❌ FFmpeg error:", e.stderr.decode())
        raise
    except Exception as e:
        print("❌ Unexpected error:", str(e))
        raise
