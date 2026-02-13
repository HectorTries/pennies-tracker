#!/usr/bin/env python3
"""
TikTok scraper for @pinkpennies_
Downloads videos, extracts audio, and transcribes.
"""

import json
import os
import subprocess
import signal
from datetime import datetime
from pathlib import Path

CREATOR = "pinkpennies_"
OUTPUT_FILE = "data/videos.json"
DATA_DIR = Path("data")

def load_existing_data():
    if Path(OUTPUT_FILE).exists():
        with open(OUTPUT_FILE) as f:
            return json.load(f)
    return {"creator": CREATOR, "videos": [], "last_updated": None}

def save_data(data):
    DATA_DIR.mkdir(exist_ok=True)
    data["last_updated"] = datetime.now().isoformat()
    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"✓ Saved {len(data['videos'])} videos to {OUTPUT_FILE}")

def get_video_urls():
    """Get latest video URLs from creator via yt-dlp."""
    print(f"🔍 Fetching videos from @{CREATOR}...")
    
    try:
        result = subprocess.run([
            "yt-dlp", "--flat-playlist", "--print", "%(id)s|%(title)s",
            f"https://www.tiktok.com/@{CREATOR}",
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            print(f"⚠️  yt-dlp failed: {result.stderr[:200]}")
            return []
        
        videos = []
        for line in result.stdout.strip().split("\n"):
            if line and "|" in line:
                parts = line.split("|")
                video_id = parts[0]
                title = parts[1] if len(parts) > 1 else "Unknown"
                videos.append({
                    "id": video_id,
                    "title": title,
                    "url": f"https://www.tiktok.com/@{CREATOR}/video/{video_id}",
                })
        
        print(f"✓ Found {len(videos)} videos")
        return videos
        
    except subprocess.TimeoutExpired:
        print("⚠️  Request timed out")
        return []
    except Exception as e:
        print(f"⚠️  Error: {e}")
        return []

def download_audio(video_url, video_id):
    """Download audio from video."""
    audio_path = DATA_DIR / f"{video_id}.mp3"
    
    if audio_path.exists():
        return str(audio_path)
    
    print(f"  ↓ Downloading audio for {video_id}...")
    
    try:
        subprocess.run([
            "yt-dlp", "-x", "--audio-format", "mp3",
            "-o", str(audio_path), video_url,
        ], capture_output=True, timeout=180)
        
        if audio_path.exists():
            return str(audio_path)
    except Exception as e:
        print(f"  ⚠️  Download failed: {e}")
    
    return None

def transcribe_audio(audio_path, video_id):
    """Transcribe audio using OpenAI Whisper."""
    if not audio_path or not os.getenv("OPENAI_API_KEY"):
        return None
    
    print(f"  🎙️  Transcribing...")
    
    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        with open(audio_path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", file=f, response_format="text"
            )
        
        text = transcript.text if hasattr(transcript, "text") else str(transcript)
        print(f"  ✓ Transcribed {len(text)} chars")
        return text
        
    except Exception as e:
        print(f"  ⚠️  Transcription failed: {e}")
        return None

def main():
    print(f"\n{'='*50}")
    print(f"🎯 Running {CREATOR} tracker")
    print(f"{'='*50}\n")
    
    data = load_existing_data()
    existing_ids = {v["id"] for v in data["videos"]}
    
    videos = get_video_urls()
    
    if not videos:
        print("⚠️  No videos found - adding placeholder")
        data["videos"].insert(0, {
            "id": "placeholder-" + datetime.now().strftime("%Y%m%d"),
            "title": "Run attempted - TikTok may be blocking",
            "url": f"https://www.tiktok.com/@{CREATOR}",
            "scraped_at": datetime.now().isoformat(),
            "transcript": None
        })
        save_data(data)
        return
    
    new_count = 0
    for video in videos[:3]:  # Limit to 3 for speed
        if video["id"] in existing_ids:
            continue
        
        print(f"\n📹 Processing: {video['title']}")
        
        audio_path = download_audio(video["url"], video["id"])
        transcript = None
        if audio_path:
            transcript = transcribe_audio(audio_path, video["id"])
        
        video_entry = {
            "id": video["id"],
            "title": video["title"],
            "url": video["url"],
            "scraped_at": datetime.now().isoformat(),
            "transcript": transcript,
        }
        
        data["videos"].insert(0, video_entry)
        new_count += 1
    
    print(f"\n✓ Found {new_count} new videos")
    save_data(data)

if __name__ == "__main__":
    main()
