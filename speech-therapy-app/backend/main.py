from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import shutil
from pathlib import Path

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
    Endpoint to receive audio file and analyze it
    """
    try:
        # Save uploaded file temporarily
        file_path = UPLOAD_DIR / audio.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
        
        # TODO: Process audio with speech recognition model
        # TODO: Analyze speech patterns
        # TODO: Send to LLM for feedback
        
        return {
            "status": "success",
            "message": "Audio received",
            "filename": audio.filename
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)