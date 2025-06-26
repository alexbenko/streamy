from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()
BASE_DIR = Path(__file__).parent
SHOWS_DIR = BASE_DIR / "shows"
MOVIES_DIR = SHOWS_DIR / "Movies"

templates = Jinja2Templates(directory="templates")

app.mount("/shows", StaticFiles(directory=SHOWS_DIR), name="shows")


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
