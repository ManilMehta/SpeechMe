from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import shutil
from pathlib import Path
from audio_processor import AudioProcessor
from speech_therapist import SpeechTherapist
from database import DatabaseManager
from auth import verify_token

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

# Initialize Supabase with service role key (for admin operations)
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

# Initialize components
print("Initializing Audio Processor...")
audio_processor = AudioProcessor()
print("Audio Processor ready!")

print("Initializing Speech Therapist AI...")
speech_therapist = SpeechTherapist()
print("Speech Therapist AI ready!")

print("Initializing Database Manager...")
db_manager = DatabaseManager(supabase)
print("Database Manager ready!")

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
async def analyze_speech(
    audio: UploadFile = File(...),
    user_id: str = Depends(verify_token)  # Now extracts real user ID from token!
):
    """
    Endpoint to receive audio file, analyze it, generate AI feedback, and save to database
    Requires authentication.
    """
    
    try:
        print(f"Processing audio for user: {user_id}")
        print(f"Received audio file: {audio.filename}")
        
        # Save uploaded file temporarily
        file_path = UPLOAD_DIR / f"temp_{user_id}_{audio.filename}"
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
        
        print("Uploading audio to Supabase Storage...")
        
        # Upload audio file to Supabase Storage
        audio_url = db_manager.upload_audio_file(
            user_id=user_id,
            file_path=str(file_path),
            filename=audio.filename
        )
        
        print("Saving session to database...")
        
        # Save session to database
        session = db_manager.save_practice_session(
            user_id=user_id,
            audio_url=audio_url,
            transcription=analysis_result["transcription"],
            word_count=analysis_result["word_count"],
            speaking_rate_wpm=analysis_result.get("speaking_rate_wpm", 0),
            audio_features=analysis_result["audio_features"],
            ai_feedback=ai_feedback
        )
        
        # Clean up temporary file
        file_path.unlink()
        
        print("✅ Complete! Session saved successfully!")
        
        # Return results
        return {
            "status": "success",
            "session_id": session["id"],
            "transcription": analysis_result["transcription"],
            "word_count": analysis_result["word_count"],
            "speaking_rate_wpm": analysis_result["speaking_rate_wpm"],
            "audio_features": analysis_result["audio_features"],
            "ai_feedback": ai_feedback,
            "score": session["score"],
            "audio_url": audio_url
        }
    
    except Exception as e:
        import traceback
        
        print("=" * 50)
        print("❌ ERROR OCCURRED")
        print("=" * 50)
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\nFull traceback:")
        print(traceback.format_exc())
        print("=" * 50)
        
        # Clean up temp file if it exists
        try:
            if 'file_path' in locals() and file_path.exists():
                file_path.unlink()
        except:
            pass
            
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions")
def get_user_sessions(
    limit: int = 10,
    user_id: str = Depends(verify_token)
):
    """
    Get recent practice sessions for the authenticated user
    """
    try:
        sessions = db_manager.get_user_sessions(user_id, limit)
        return {
            "status": "success",
            "sessions": sessions,
            "count": len(sessions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
def get_user_stats(user_id: str = Depends(verify_token)):
    """
    Get overall statistics for the authenticated user
    """
    try:
        stats = db_manager.get_user_stats(user_id)
        return {
            "status": "success",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)