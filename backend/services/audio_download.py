import yt_dlp
import os

def download_audio(youtube_url, out_dir="tmp"):
    os.makedirs(out_dir, exist_ok=True)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(out_dir, '%(id)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=True)
        filename = ydl.prepare_filename(info)
        base, _ = os.path.splitext(filename)
        wav_path = base + ".wav"
        return wav_path, {
            "title": info.get("title"),
            "duration": info.get("duration"),
            "id": info.get("id"),
        }
