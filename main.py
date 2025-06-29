from fastapi import FastAPI, Request, HTTPException, Response, Form, UploadFile, File
from fastapi.responses import RedirectResponse
import shutil
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import subprocess
app = FastAPI()
BASE_DIR = Path(__file__).parent
SHOWS_DIR = BASE_DIR / "shows"
MOVIES_DIR = SHOWS_DIR / "Movies"

templates = Jinja2Templates(directory="templates")

app.mount("/shows", StaticFiles(directory=SHOWS_DIR), name="shows")
def get_show_season_structure():
    structure = {}
    for show_dir in SHOWS_DIR.iterdir():
        if show_dir.is_dir() and show_dir.name.lower() != "movies":
            seasons = [season.name for season in show_dir.iterdir() if season.is_dir()]
            structure[show_dir.name] = sorted(seasons)
    return structure
@app.get("/upload")
def upload_page(request: Request):
    show_structure = get_show_season_structure()
    return templates.TemplateResponse("upload.html", {
        "request": request,
        "show_structure": show_structure
    })


@app.get("/")
def home(request: Request):
    entries = []

    for entry_dir in SHOWS_DIR.iterdir():
        if not entry_dir.is_dir():
            continue

        is_movie = any(f.suffix == ".mp4" for f in entry_dir.iterdir())

        entries.append({
            "name": entry_dir.name,
            "is_movie": is_movie,
            "thumbnail": f"/shows/{entry_dir.name}/thumbnail.jpeg"
        })

    return templates.TemplateResponse("index.html", {
        "request": request,
        "entries": sorted(entries, key=lambda x: x["name"].lower())
    })


@app.get("/Movies")
def list_all_movies(request: Request):
    if not MOVIES_DIR.exists() or not MOVIES_DIR.is_dir():
        raise HTTPException(status_code=404, detail="Movies folder missing")

    movie_files = [f.name for f in MOVIES_DIR.glob("*.mp4")]

    return templates.TemplateResponse("episodes.html", {
        "request": request,
        "show": "Movies",
        "season": None,
        "episodes": sorted(movie_files),
        "is_movie": True
    })




@app.get("/{entry_name}/{second}")
def handle_show_or_movie_file(entry_name: str, second: str, request: Request):
    entry_dir = SHOWS_DIR / entry_name
    full_path = entry_dir / second

    if not entry_dir.exists():
        raise HTTPException(status_code=404, detail="Entry not found")

    # If it's a video file, render player
    if full_path.suffix == ".mp4" and full_path.is_file():
        return templates.TemplateResponse("watch.html", {
            "request": request,
            "title": f"{entry_name} - {second}",
            "stream_type": "shows",
            "video_url": f"{entry_name}/{second}"
        })

    # If it's a directory (season), render episode list
    if full_path.is_dir():
        episodes = [
            f.name for f in full_path.iterdir()
            if f.suffix == ".mp4"
        ]
        return templates.TemplateResponse("episodes.html", {
            "request": request,
            "show": entry_name,
            "season": second,
            "episodes": sorted(episodes)
        })

    raise HTTPException(status_code=404, detail="Not found")


@app.get("/{show_name}/{season}/{episode}")
def episode_player(show_name: str, season: str, episode: str, request: Request):
    file_path = SHOWS_DIR / show_name / season / episode
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Episode not found")

    return templates.TemplateResponse("watch.html", {
        "request": request,
        "title": f"{show_name} - {season} - {episode}",
        "stream_type": "shows",
        "video_url": f"{show_name}/{season}/{episode}"
    })


@app.get("/stream/{type}/{path:path}")
def stream_video(type: str, path: str, request: Request):
    if type not in ("shows", "movies"):
        raise HTTPException(status_code=404)

    file_path = SHOWS_DIR / path if type == "shows" else MOVIES_DIR / path

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    file_size = file_path.stat().st_size
    range_header = request.headers.get("range")
    start = 0
    end = file_size - 1

    if range_header:
        bytes_range = range_header.replace("bytes=", "").split("-")
        if bytes_range[0]:
            start = int(bytes_range[0])
        if len(bytes_range) > 1 and bytes_range[1]:
            end = int(bytes_range[1])
        if start >= file_size or start > end:
            return Response(status_code=416)

    def iterfile():
        with open(file_path, "rb") as f:
            f.seek(start)
            remaining = end - start + 1
            chunk_size = 1024 * 1024
            while remaining > 0:
                chunk = f.read(min(chunk_size, remaining))
                if not chunk:
                    break
                yield chunk
                remaining -= len(chunk)

    headers = {
        "Content-Type": "video/mp4",
        "Accept-Ranges": "bytes",
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Content-Length": str(end - start + 1),
    }

    return StreamingResponse(iterfile(), headers=headers, status_code=206 if range_header else 200)


@app.get("/{entry_name}")
def entry_page(entry_name: str, request: Request):
    entry_path = SHOWS_DIR / entry_name

    if not entry_path.exists() or not entry_path.is_dir():
        raise HTTPException(status_code=404, detail="Entry not found")

    # Movie folder (contains mp4s directly)
    mp4s = [f for f in entry_path.iterdir() if f.suffix == ".mp4"]
    if mp4s:
        if len(mp4s) == 1:
            return templates.TemplateResponse("watch.html", {
                "request": request,
                "title": entry_name,
                "stream_type": "shows",
                "video_url": f"{entry_name}/{mp4s[0].name}"
            })
        else:
            return templates.TemplateResponse("episodes.html", {
                "request": request,
                "show": entry_name,
                "season": None,
                "episodes": [f.name for f in mp4s]
            })

    # TV show folder (contains season directories)
    seasons = [d.name for d in entry_path.iterdir() if d.is_dir()]
    return templates.TemplateResponse("seasons.html", {
        "request": request,
        "show": entry_name,
        "seasons": sorted(seasons)
    })




@app.post("/upload")
async def upload_handler(
    request: Request,
    type: str = Form(...),
    movie_name: str = Form(None),
    show_name: str = Form(None),
    new_show: str = Form(None),
    season: str = Form(None),
    new_season: str = Form(None),
    episode: str = Form(None),
    video: UploadFile = Form(...),
    thumb_time: int = Form(55),
):
    if type == "movie":
        movie_dir = MOVIES_DIR
        movie_dir.mkdir(parents=True, exist_ok=True)
        dest_path = movie_dir / f"{movie_name}.mp4"
        thumb_path = movie_dir / f"{movie_name}-thumbnail.jpeg"
    elif type == "show":
        final_show = new_show if show_name == "_new" else show_name
        final_season = new_season if season == "_new" else season

        if not final_show or not final_season or not episode:
            raise HTTPException(status_code=400, detail="Missing show, season, or episode")

        dest_dir = SHOWS_DIR / final_show / final_season
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / episode
        thumb_path = dest_dir / f"{Path(episode).stem}-thumbnail.jpeg"
    else:
        raise HTTPException(status_code=400, detail="Invalid type")

    # Save uploaded video
    with dest_path.open("wb") as f:
        shutil.copyfileobj(video.file, f)

    # Generate thumbnail using ffmpeg
    try:
        subprocess.run([
            "ffmpeg",
            "-ss", str(thumb_time),
            "-i", str(dest_path),
            "-vframes", "1",
            "-q:v", "2",
            str(thumb_path)
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print(f"Thumbnail generation failed for {dest_path}")

    return RedirectResponse(url="/", status_code=303)

def generate_missing_thumbnails():
    print("🔍 Scanning for missing thumbnails...")

    for entry in SHOWS_DIR.iterdir():
        if not entry.is_dir():
            continue

        # Handle movies
        if entry.name.lower() == "movies":
            for mp4 in entry.glob("*.mp4"):
                generate_thumb_if_missing(mp4)
            continue

        # Handle shows with seasons
        for season in entry.iterdir():
            if not season.is_dir():
                continue
            for mp4 in season.glob("*.mp4"):
                generate_thumb_if_missing(mp4)

    print("✅ Thumbnail check complete.")

def generate_thumb_if_missing(mp4_path: Path):
    thumb_path = mp4_path.with_name(mp4_path.stem + "-thumbnail.jpg")
    if thumb_path.exists():
        return

    print(f"🎞️  Generating thumbnail for: {mp4_path.relative_to(SHOWS_DIR.parent)}")
    cmd = [
        "ffmpeg",
        "-loglevel", "error",
        "-ss", "00:00:55",
        "-i", str(mp4_path),
        "-frames:v", "1",
        "-q:v", "2",
        str(thumb_path)
    ]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        print(f"⚠️ Failed to generate thumbnail for {mp4_path}")

if __name__ == "__main__":
    import uvicorn
    generate_missing_thumbnails()
    uvicorn.run(app, host="0.0.0.0", port=8000)
