#!/usr/bin/env python3
print("Python is working!")
import json
import os
from pathlib import Path

print(f"Current dir: {os.getcwd()}")
print(f"Files: {os.listdir('.')}")

# Create data dir
Path("data").mkdir(exist_ok=True)

# Write file
data = {"test": "hello", "time": str(os.times())}
with open("data/test.json", "w") as f:
    json.dump(data, f)

print("Wrote test.json")
print(f"Files in data: {os.listdir('data')}")
