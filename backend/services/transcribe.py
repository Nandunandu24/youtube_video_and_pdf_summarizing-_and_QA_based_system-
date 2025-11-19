# services/transcribe.py
import os
import json
import whisper
from services.audio_download import download_audio


def transcribe_and_index(
    youtube_url: str,
    model_name: str = "tiny",
    transcripts_root: str = "transcripts"
):
    """
    Step 1: Download audio
    Step 2: Transcribe using Whisper
    Step 3: Save transcript
    RETURN ONLY transcript — FAISS is built later in youtube/process route.
    """

    # Download audio
    print(f"🎬 Downloading audio: {youtube_url}")
    wav_path, info = download_audio(youtube_url)
    video_id = info.get("id", "unknown")

    # Block long videos
    if info.get("duration") and info["duration"] > 1200:
        raise MemoryError("🚫 Video too long (>20 min).")

    # Transcribe
    print("🎧 Transcribing audio (Whisper tiny)...")
    model = whisper.load_model(model_name)
    result = model.transcribe(wav_path, verbose=False, fp16=False)

    segments = result.get("segments", [])
    if not segments:
        raise RuntimeError("❌ Whisper failed to generate segments")

    # Save transcript
    video_tr_dir = os.path.join(transcripts_root, video_id)
    os.makedirs(video_tr_dir, exist_ok=True)

    transcript_path = os.path.join(video_tr_dir, "transcript.json")
    with open(transcript_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"✅ Transcript saved: {transcript_path}")

    # Return ONLY basic info
    return {
        "status": "success",
        "video_id": video_id,
        "transcript_path": transcript_path,
        "segments_count": len(segments)
    }
