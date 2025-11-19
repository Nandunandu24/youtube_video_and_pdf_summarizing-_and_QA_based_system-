# tests/test_transcribe.py
from services.audio_download import download_audio
from services.transcribe import transcribe

def test_transcribe():
    url = "https://www.youtube.com/watch?v=tLKKmouUams"  # sample video
    wav, info = download_audio(url)
    res = transcribe(wav, model_name="small")

    print("Video Title:", info["title"])
    print("Full text length:", len(res["text"]))
    print("Segments count:", len(res["segments"]))
    print("Sample segment:", res["segments"][0])
