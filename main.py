from fastapi import FastAPI, File, UploadFile
import whisper
import tempfile
import shutil
import os


app = FastAPI()


model = whisper.load_model("base")


@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    if file.content_type not in ["audio/mpeg", "audio/wav", "audio/x-wav", "audio/mp4", "audio/webm"]:
        return {"error": f"Unsupported file type: {file.content_type}"}

    filename = file.filename.lower()
    if not filename.endswith((".mp3", ".wav", ".m4a", ".webm")):
        return {"error": "Only mp3, wav, m4a, and webm files are supported."}

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[-1]) as temp_audio:
            shutil.copyfileobj(file.file, temp_audio)
            temp_audio_path = temp_audio.name

        result = model.transcribe(temp_audio_path)
        os.remove(temp_audio_path)

        return {"transcription": result["text"]}

    except Exception as e:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        return {"error": f"Transcription failed: {str(e)}"}
