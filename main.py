from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()
BASE_DIR = Path(__file__).parent
SHOWS_DIR = BASE_DIR / "shows"
MOVIES_DIR = BASE_DIR / "shows" / "movies"

templates = Jinja2Templates(directory="templates")



@app.get("/")
def home(request: Request):
    shows = []
    for show_dir in SHOWS_DIR.iterdir():
        if show_dir.is_dir():
            shows.append({
                "name": show_dir.name,
                "thumbnail": f"/shows/{show_dir.name}/thumbnail.jpeg"
            })

    movies = []
    for movie_path in MOVIES_DIR.glob("*.mp4"):
        name = movie_path.stem
        thumb_path = MOVIES_DIR / name / "thumbnail.jpeg"
        movies.append({
            "name": name,
            "thumbnail": f"/movies/{name}/thumbnail.jpeg" if thumb_path.exists() else None
        })

    return templates.TemplateResponse("index.html", {
        "request": request,
        "shows": shows,
        "movies": movies
    })


@app.get("/Movies/{movie_name}")
def movie_page(movie_name: str, request: Request):
    file_path = MOVIES_DIR / f"{movie_name}.mp4"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Movie not found")

    return templates.TemplateResponse("watch.html", {
        "request": request,
        "title": movie_name,
        "video_url": f"/movies/{movie_name}.mp4"
    })


@app.get("/{show_name}")
def show_seasons(show_name: str, request: Request):
    show_path = SHOWS_DIR / show_name
    if not show_path.exists() or not show_path.is_dir():
        raise HTTPException(status_code=404, detail="Show not found")

    seasons = []
    for season_dir in show_path.iterdir():
        if season_dir.is_dir():
            seasons.append(season_dir.name)

    return templates.TemplateResponse("seasons.html", {
        "request": request,
        "show": show_name,
        "seasons": sorted(seasons)
    })


@app.get("/{show_name}/{season}")
def season_episodes(show_name: str, season: str, request: Request):
    season_path = SHOWS_DIR / show_name / season
    if not season_path.exists() or not season_path.is_dir():
        raise HTTPException(status_code=404, detail="Season not found")

    episodes = [
        file.name for file in season_path.iterdir()
        if file.suffix == ".mp4"
    ]

    return templates.TemplateResponse("episodes.html", {
        "request": request,
        "show": show_name,
        "season": season,
        "episodes": sorted(episodes)
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
        # Parse Range header
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



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)