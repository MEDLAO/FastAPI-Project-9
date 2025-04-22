from fastapi import FastAPI, File, UploadFile
import whisper
import tempfile
import shutil


app = FastAPI()

# Load the whisper model once
model = whisper.load_model("base")  # "tiny", "base", "small", "medium", "large"


@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    # Save uploaded file to a temp location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        shutil.copyfileobj(file.file, temp_audio)
        temp_audio_path = temp_audio.name

    # Transcribe with whisper
    result = model.transcribe(temp_audio_path)

    return {"transcription": result["text"]}
