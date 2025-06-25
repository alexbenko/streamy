# --- Stage 1: Build the frontend ---
FROM node:lts AS frontend

WORKDIR /web
COPY web/package*.json ./
RUN npm install
COPY web/ ./
RUN npm run build


# --- Stage 2: Python backend + static build ---
FROM python:3.13 AS backend

WORKDIR /

# Optional: install ffmpeg if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY . .

# Copy built frontend into FastAPI's static folder
RUN mkdir -p dist
COPY --from=frontend /web/dist ./dist

# Expose FastAPI port
EXPOSE 4200

# Run FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "4200"]
