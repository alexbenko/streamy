#!/usr/bin/env python3
"""
Generate thumbnails for every .mp4 in /shows
Usage:  python make_thumbs.py  /path/to/shows
"""
import subprocess
from pathlib import Path
import sys

# ---------- config ----------
TIMESTAMP = "00:00:55"          # position to grab frame
THUMB_SUFFIX = "-thumbnail.jpg" # output suffix
QUALITY = "2"                   # ffmpeg -q:v value (1–31 lower=better)
# -----------------------------

def make_thumbnail(video: Path):
    thumb = video.with_suffix("").with_name(video.stem + THUMB_SUFFIX)
    if thumb.exists():
        print("✓ exists:", thumb.relative_to(BASE))
        return

    thumb_cmd = [
        "ffmpeg",
        "-loglevel", "error",      # quiet, only errors
        "-ss", TIMESTAMP,          # seek
        "-i", str(video),          # input
        "-frames:v", "1",          # one frame
        "-q:v", QUALITY,           # quality
        str(thumb)                 # output
    ]

    try:
        subprocess.run(thumb_cmd, check=True)
        print("✔ created:", thumb.relative_to(BASE))
    except subprocess.CalledProcessError as e:
        print("⚠ ffmpeg failed for", video, ":", e)

def walk_shows(root: Path):
    movies_dir = root / "Movies"

    # --- Movies ---
    if movies_dir.exists():
        for mp4 in movies_dir.glob("*.mp4"):
            make_thumbnail(mp4)

    # --- TV Shows ---
    for show_dir in root.iterdir():
        if not show_dir.is_dir() or show_dir.name == "Movies":
            continue
        for season_dir in show_dir.iterdir():
            if not season_dir.is_dir():
                continue
            for mp4 in season_dir.glob("*.mp4"):
                make_thumbnail(mp4)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python make_thumbs.py /path/to/shows")
        sys.exit(1)

    BASE = Path(sys.argv[1]).expanduser().resolve()
    if not BASE.exists():
        print("Folder not found:", BASE)
        sys.exit(1)

    walk_shows(BASE)
    print("Done.")
