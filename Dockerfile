FROM python:3.9-slim
WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg

RUN pip install --upgrade pip && \
    pip install fastapi uvicorn faster-whisper numpy librosa python-multipart

COPY main.py .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
