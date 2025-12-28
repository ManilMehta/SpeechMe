from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import shutil
from pathlib import Path
from audio_processor import AudioProcessor
from speech_therapist import SpeechTherapist

load_dotenv()

app = FastAPI(title="Speech Therapy API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Initialize Audio Processor
print("Initializing Audio Processor...")
audio_processor = AudioProcessor()
print("Audio Processor ready!")

# Initialize Speech Therapist (Llama)
print("Initializing Speech Therapist AI...")
speech_therapist = SpeechTherapist()
print("Speech Therapist AI ready!")

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "Speech Therapy API is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/analyze-speech")
async def analyze_speech(audio: UploadFile = File(...)):
    """
    Endpoint to receive audio file, analyze it, and generate AI feedback
    """
    try:
        print(f"Received audio file: {audio.filename}")
        
        # Save uploaded file temporarily
        file_path = UPLOAD_DIR / f"temp_{audio.filename}"
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
        
        print("Processing audio with Whisper...")
        
        # Process audio with Whisper
        analysis_result = audio_processor.process_audio(str(file_path))
        
        print("Generating AI feedback with Llama...")
        
        # Generate personalized feedback with Llama
        ai_feedback = speech_therapist.generate_feedback(
            transcription=analysis_result["transcription"],
            audio_features=analysis_result["audio_features"],
            speaking_rate_wpm=analysis_result.get("speaking_rate_wpm", 0),
            word_count=analysis_result["word_count"]
        )
        
        # Clean up temporary file
        file_path.unlink()
        
        print("Analysis complete!")
        
        # Return results
        return {
            "status": "success",
            "transcription": analysis_result["transcription"],
            "word_count": analysis_result["word_count"],
            "speaking_rate_wpm": analysis_result["speaking_rate_wpm"],
            "audio_features": analysis_result["audio_features"],
            "ai_feedback": ai_feedback,  # This is the new AI-generated feedback!
        }
    
    except Exception as e:
        print(f"Error processing audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)