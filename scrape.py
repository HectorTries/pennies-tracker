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

# Timeout handler
class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")

# Set alarm for 45 seconds
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(45)

# Config
CREATOR = "pinkpennies_"
OUTPUT_FILE = "data/videos.json"
DATA_DIR = Path("data")

def load_existing_data():
    """Load existing video data if available."""
    if Path(OUTPUT_FILE).exists():
        with open(OUTPUT_FILE) as f:
            return json.load(f)
    return {"creator": CREATOR, "videos": [], "last_updated": None}

def save_data(data):
    """Save video data to JSON."""
    DATA_DIR.mkdir(exist_ok=True)
    data["last_updated"] = datetime.now().isoformat()
    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"✓ Saved {len(data['videos'])} videos to {OUTPUT_FILE}")

def get_video_urls():
    """Get latest video URLs from creator (via yt-dlp)."""
    print(f"🔍 Fetching videos from @{CREATOR}...")
    
    # Try to get the TikTok channel URL
    # Note: TikTok scraping is flaky - we use yt-dlp which tries multiple methods
    try:
        result = subprocess.run([
            "yt-dlp",
            "--flat-playlist",
            "--print", "%(id)s|%(title)s|%(duration)s|%(upload_date)s",
            f"https://www.tiktok.com/@{CREATOR}",
            "--user-agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "--extractor-args", "tiktok:watermark=0",
            "--no-warnings",
            "--socket-timeout", "30",
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            print(f"⚠️  yt-dlp failed: {result.stderr}")
            # Try alternative method
            return get_video_urls_alternative()
        
        videos = []
        for line in result.stdout.strip().split("\n"):
            if line and "|" in line:
                parts = line.split("|")
                if len(parts) >= 2:
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
        print("⚠️  Request timed out - trying alternative...")
        return get_video_urls_alternative()
    except Exception as e:
        print(f"⚠️  Error: {e}")
        return []

def get_video_urls_alternative():
    """Try alternative method - scrape TikTok via mobile API"""
    print("🔄 Trying alternative method...")
    
    # Try with mobile API
    try:
        result = subprocess.run([
            "yt-dlp",
            "--flat-playlist", 
            "--print", "%(id)s|%(title)s",
            "--extractor-args", "tiktok:api_url=api16-normal-c-useast2a.tiktokv.com",
            f"https://www.tiktok.com/@{CREATOR}",
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 and result.stdout.strip():
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
            if videos:
                print(f"✓ Found {len(videos)} videos via alternative")
                return videos
    except Exception as e:
        print(f"  Alternative failed: {e}")
    
    print("⚠️  All methods failed - TikTok is likely blocking the IP")
    return []

def download_audio(video_url, video_id):
    """Download audio from video."""
    audio_path = DATA_DIR / f"{video_id}.mp3"
    
    if audio_path.exists():
        print(f"  ✓ Audio already exists: {video_id}.mp3")
        return str(audio_path)
    
    print(f"  ↓ Downloading audio for {video_id}...")
    
    try:
        subprocess.run([
            "yt-dlp",
            "-x",  # Extract audio
            "--audio-format", "mp3",
            "-o", str(audio_path),
            video_url,
        ], capture_output=True, timeout=300)
        
        if audio_path.exists():
            print(f"  ✓ Downloaded: {video_id}.mp3")
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
                model="whisper-1",
                file=f,
                response_format="text"
            )
        
        text = transcript.text if hasattr(transcript, "text") else str(transcript)
        print(f"  ✓ Transcribed {len(text)} chars")
        return text
        
    except Exception as e:
        print(f"  ⚠️  Transcription failed: {e}")
        return None

def main():
    try:
        print(f"\n{'='*50}")
        print(f"🎯 Running {CREATOR} tracker")
        print(f"{'='*50}\n")
        
        # First - always write test data to prove workflow works
        print("Loading existing data...")
        data = load_existing_data()
        
        print("Creating test entry...")
        test_entry = {
            "id": "test-" + datetime.now().strftime("%Y%m%d-%H%M%S"),
            "title": "Workflow test - " + datetime.now().isoformat(),
            "url": "https://www.tiktok.com/@" + CREATOR,
            "scraped_at": datetime.now().isoformat(),
            "transcript": "Test entry to prove GitHub Actions works."
        }
        data["videos"].insert(0, test_entry)
        
        print("Saving data...")
        save_data(data)
        print("✓ Wrote test entry")
        
        # Then try TikTok (will likely timeout/block, but we already saved)
        print("🔍 Attempting TikTok fetch (may timeout)...")
        videos = get_video_urls()
        
        if videos:
            print(f"✓ Found {len(videos)} videos")
            # Process them...
        else:
            print("⚠️  TikTok blocked or no videos found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Process new videos
    new_count = 0
    for video in videos:
        if video["id"] in existing_ids:
            continue
        
        print(f"\n📹 Processing: {video['title']}")
        
        # Download audio
        audio_path = download_audio(video["url"], video["id"])
        
        # Transcribe
        transcript = None
        if audio_path:
            transcript = transcribe_audio(audio_path, video["id"])
        
        # Add to data
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
    print(f"\n🎉 Done! Total videos: {len(data['videos'])}")

if __name__ == "__main__":
    main()
