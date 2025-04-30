from fastapi import FastAPI, File, UploadFile
import whisper
import tempfile
import shutil
import os


app = FastAPI()

model = whisper.load_model("base")


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/")
def read_root():
    welcome_message = (
        "Welcome!"
        "¡Bienvenido!"
        "欢迎!"
        "नमस्ते!"
        "مرحبًا!"
        "Olá!"
        "Здравствуйте!"
        "Bonjour!"
        "বাংলা!"
        "こんにちは!"
    )
    return {"message": welcome_message}


# Transcribe full audio to text
@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    # Check for supported MIME types
    if file.content_type not in ["audio/mpeg", "audio/wav", "audio/x-wav", "audio/mp4", "audio/webm"]:
        return {"error": f"Unsupported file type: {file.content_type}"}

    # Check file extension
    filename = file.filename.lower()
    if not filename.endswith((".mp3", ".wav", ".m4a", ".webm")):
        return {"error": "Only mp3, wav, m4a, and webm files are supported."}

    try:
        # Save uploaded audio to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[-1]) as temp_audio:
            shutil.copyfileobj(file.file, temp_audio)
            temp_audio_path = temp_audio.name

        # Transcribe audio using Whisper
        result = model.transcribe(temp_audio_path)

        # Remove temporary file
        os.remove(temp_audio_path)

        # Return full transcription text
        return {"transcription": result["text"]}

    except Exception as e:
        # Clean up temp file in case of error
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        return {"error": f"Transcription failed: {str(e)}"}


# Return transcription segments with timestamps
@app.post("/segments/")
async def get_segments(file: UploadFile = File(...)):
    # Get and normalize file name
    filename = file.filename.lower()

    try:
        # Save uploaded audio to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[-1]) as temp_audio:
            shutil.copyfileobj(file.file, temp_audio)
            temp_audio_path = temp_audio.name

        # Transcribe audio using Whisper
        result = model.transcribe(temp_audio_path)

        # Remove temporary file
        os.remove(temp_audio_path)

        # Extract and format segments: start time, end time, and text
        segments = [
            {"start": round(seg["start"], 2), "end": round(seg["end"], 2), "text": seg["text"]}
            for seg in result.get("segments", [])
        ]

        return {"segments": segments}

    except Exception as e:
        # Clean up temp file in case of error
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        return {"error": f"Segment extraction failed: {str(e)}"}
