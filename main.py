import os
import tempfile
import warnings
import logging
import numpy as np
import librosa
import subprocess

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader
from faster_whisper import WhisperModel

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_KEY = os.getenv("API_KEY", "default_api_key")
API_KEY_NAME = "Authorization"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

model_name = os.getenv("MODEL", "base")
device = "cuda" if os.getenv("USE_CUDA", "false").lower() == "true" else "cpu"
compute_type = "int8" if device=="cpu" else "float16"
model = WhisperModel(model_name, device=device, compute_type=compute_type)
threshold_db = float(os.getenv("THRESHOLD_DB", "-50"))
language = os.getenv("LANGUAGE", "ja")

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...), api_key: str = Depends(verify_api_key)):
    audio_bytes = await file.read()

    with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as tmp_in:
        tmp_in.write(audio_bytes)
        tmp_in.flush()
        input_path = tmp_in.name

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_out:
        output_path = tmp_out.name

    ffmpeg_command = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-ar", "16000",
        "-ac", "1",
        output_path
    ]
    subprocess.run(ffmpeg_command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    y, sr = librosa.load(output_path, sr=None)
    rms = np.sqrt(np.mean(y**2))
    db = 20 * np.log10(rms + 1e-6)
    if db < threshold_db:
        return {"text": ""}

    segments, info = model.transcribe(output_path, beam_size=5, language=language)
    text = "".join(seg.text for seg in segments)
    return {"text": text}
