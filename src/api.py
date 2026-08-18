import os
import shutil
import tempfile
import sys

sys.path.append(os.path.dirname(__file__))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from extract_audio import extract_audio
from fingerprint import fingerprint
from index import FingerprintIndex
from match import identify

app = FastAPI(title="Shazam for Movies API")

# Allow requests from your mobile app (loosen for MVP, tighten later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "data/fingerprints.db"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/identify")
async def identify_clip(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    with tempfile.TemporaryDirectory() as tmp_dir:
        # save uploaded file (could be audio or video)
        input_path = os.path.join(tmp_dir, file.filename)
        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        wav_path = os.path.join(tmp_dir, "query.wav")

        try:
            extract_audio(input_path, wav_path)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Audio extraction failed: {e}")

        idx = FingerprintIndex(DB_PATH)
        try:
            result = identify(wav_path, idx, fingerprint)
        finally:
            idx.close()

        if result is None:
            return {"match": False, "message": "No confident match found."}

        return {
            "match": True,
            "track_id": result["track_id"],
            "score": result["score"],
            "offset_frames": int(result["offset_frames"]),
        }
