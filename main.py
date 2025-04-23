from fastapi import FastAPI, File, UploadFile
import whisper
import tempfile
import shutil
import os


app = FastAPI()

# Load the Whisper model once at startup
model = whisper.load_model("base")


@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    # Save uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        # Copy the uploaded audio file to the temporary file location
        shutil.copyfileobj(file.file, temp_audio)

        # Store the path of the temporary audio file for transcription
        temp_audio_path = temp_audio.name

    # Transcribe the audio file using Whisper
    result = model.transcribe(temp_audio_path)

    # Clean up the temporary file
    os.remove(temp_audio_path)

    return {"transcription": result["text"]}
