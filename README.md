# 🎬 FastAPI Media Server

A lightweight, directory-based media server built with **FastAPI**, serving TV shows and movies directly from your file system. It supports streaming `.mp4` files with automatic thumbnail generation via `ffmpeg` and a modern dark-mode friendly UI — all without a database.

---

## 🚀 Features

- 📂 **Directory-based UI** — No config or metadata files needed
- 🔍 **Auto thumbnail generation** using `ffmpeg`
- 📺 **TV Shows with seasons and episodes**
- 🎞 **Movies with or without folders**
- 🌗 **Automatic dark mode**
- 🔥 **Streams video using HTTP Range requests**
- 📱 Fully accessible over your local network

---

## 🛠 Tech Stack

- **FastAPI** — Python web framework
- **Jinja2** — Template rendering
- **Vanilla JS/CSS** — No frontend frameworks
- **ffmpeg** — Generates thumbnails from videos

---

## 📁 Directory Structure

Just drop your media into the `shows/` folder:

```
shows/
├── Invincible/
│   └── season_1/
│       ├── ep1.mp4
│       └── ep2.mp4
├── Rick and Morty/
│   └── season_2/
│       ├── ep1.mp4
│       └── ep2.mp4
├── Movies/
│   ├── Spider-Man.mp4
│   └── Interstellar.mp4
```

- Each video can optionally include a `<filename>-thumbnail.jpg`
- Movies live in the `/Movies` folder with `.mp4` files directly
- TV shows follow `/Show/Season/Episode.mp4`

---

## ⚙️ Setup

### 1. Install dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Install ffmpeg

```bash
sudo apt update
sudo apt install ffmpeg -y
```

### 3. Run the server

```bash
python main.py
```

Access the app at:
http://localhost:8000 or http://<your-pi-ip>:8000 from another device on the network.

---

## 📸 Thumbnails

On startup, the app:
- Scans all media files
- Generates thumbnails if `*-thumbnail.jpg` is missing
- Uses the 5-second mark for thumbnail extraction

Thumbnails are saved next to the video file automatically.

---

## 📦 Deployment (optional with pm2)

```bash
pip install uvicorn
pm2 start main.py --interpreter python3
```

---

## 📝 License

MIT — Free to use, fork, and hack on.
