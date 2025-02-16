FROM docker.io/nvidia/cuda:12.8.0-cudnn-runtime-ubuntu22.04
WORKDIR /app

RUN apt-get update && apt-get install -y python3 python3-pip ffmpeg

RUN pip3 install --upgrade pip && \
    pip3 install fastapi uvicorn faster-whisper numpy librosa python-multipart

COPY main.py .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
