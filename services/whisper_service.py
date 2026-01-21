import whisper
import os
import traceback

def transcribe_audio(audio_path: str):
    try:
        audio_path = os.path.abspath(audio_path)
        if not os.path.exists(audio_path):
            raise FileNotFoundError(audio_path)

        print("🧠 Loading Whisper model inside process...")
        model = whisper.load_model("base", device="cpu")

        print(f"🔹 Transcribing audio: {audio_path}")
        result = model.transcribe(
            audio_path,
            fp16=False,
            verbose=False
        )

        segments = []
        for seg in result.get("segments", []):
            segments.append({
                "time": f"{int(seg['start']//60)}:{int(seg['start']%60):02d}",
                "text": seg["text"].strip()
            })

        print(f"✅ Transcription complete: {len(segments)} segments")
        return segments

    except Exception:
        print("❌ Whisper transcription failed")
        traceback.print_exc()
        return []
