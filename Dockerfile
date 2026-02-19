# ==========================================
# Phase 1: Build the Frontend (React)
# ==========================================
FROM node:18-alpine as build-stage

WORKDIR /app
COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
# We set VITE_API_URL to empty so it uses relative paths in production
ENV VITE_API_URL=""
RUN npm run build

# ==========================================
# Phase 2: Setup the Backend (Flask)
# ==========================================
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy backend code
COPY backend/ .

# Copy built frontend from Stage 1 to the backend's static folder
# Note: app.py is configured to look for 'static' in its directory
COPY --from=build-stage /app/dist /app/static

# Environment variables
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1
ENV PORT=5001

EXPOSE 5001

# Run gunicorn
# Render provides the PORT env var, we use a shell form to expand it
CMD gunicorn --bind 0.0.0.0:${PORT:-5001} --workers 1 --threads 2 --timeout 300 "app:create_app()"
