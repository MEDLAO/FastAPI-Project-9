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
    # ✅ Validate file content type (MIME type)
    if file.content_type not in ["audio/mpeg", "audio/wav", "audio/x-wav", "audio/mp4", "audio/webm"]:
        return JSONResponse(status_code=400, content={"error": f"Unsupported file type: {file.content_type}"})

    # ✅ Validate file extension (optional but recommended)
    filename = file.filename.lower()
    if not filename.endswith((".mp3", ".wav", ".m4a", ".webm")):
        return JSONResponse(status_code=400, content={"error": "Only mp3, wav, m4a, and webm files are supported."})

    try:
        # Save uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[-1]) as temp_audio:
            # Copy the uploaded audio file to the temporary file location
            shutil.copyfileobj(file.file, temp_audio)

            # Store the path of the temporary audio file for transcription
            temp_audio_path = temp_audio.name

        # Transcribe the audio file using Whisper
        result = model.transcribe(temp_audio_path)

        # Clean up the temporary file
        os.remove(temp_audio_path)

        return {"transcription": result["text"]}

    except Exception as e:
        # Clean up in case of any error
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        return JSONResponse(status_code=500, content={"error": f"Transcription failed: {str(e)}"})

