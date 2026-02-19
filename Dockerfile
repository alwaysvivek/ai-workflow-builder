FROM python:3.12-slim

WORKDIR /app

# Install system dependencies (gcc might be needed for some python packages)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

COPY backend/ .

# Environment variables
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

EXPOSE 5001

# Run gunicorn
# 1 worker is safer for SQLite if not using WAL mode, but concurrency is low anyway.
# 4 workers with threads=2 is standard for Sync workers.
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "1", "--threads", "2", "--timeout", "300", "app:create_app()"]
