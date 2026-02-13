#!/usr/bin/env python3
"""Simple test scraper."""

import json
import os
from datetime import datetime

print("Starting scraper...")

# Load existing or create new
import pathlib
if pathlib.Path("data/videos.json").exists():
    with open("data/videos.json") as f:
        data = json.load(f)
    print(f"Loaded existing data: {len(data.get('videos', []))} videos")
else:
    data = {"creator": "pinkpennies_", "videos": [], "last_updated": None}
    print("Created new data structure")

# Add a test entry
entry = {
    "id": "test-" + datetime.now().strftime("%Y%m%d-%H%M%S"),
    "title": "Test - " + datetime.now().isoformat(),
    "url": "https://www.tiktok.com/@pinkpennies_",
    "scraped_at": datetime.now().isoformat(),
    "transcript": "Test transcript"
}

data["videos"].insert(0, entry)
data["last_updated"] = datetime.now().isoformat()

# Save
import pathlib
pathlib.Path("data").mkdir(exist_ok=True)
with open("data/videos.json", "w") as f:
    json.dump(data, f, indent=2)

print(f"✓ Saved! Total videos: {len(data['videos'])}")
print(f"✓ File exists: {pathlib.Path('data/videos.json').exists()}")

# Verify
with open("data/videos.json") as f:
    verify = json.load(f)
print(f"✓ Verified: {len(verify['videos'])} videos in file")
