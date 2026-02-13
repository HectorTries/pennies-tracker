#!/usr/bin/env python3
print("Python is working!")
import json
import os
from pathlib import Path

# Write directly to videos.json
data = {"creator": "pinkpennies_", "videos": [{"id": "test-1", "title": "Test Video"}], "last_updated": "2026-01-01"}

Path("data").mkdir(exist_ok=True)
with open("data/videos.json", "w") as f:
    json.dump(data, f, indent=2)

print("Wrote videos.json!")
