from supabase import Client
from datetime import datetime
from typing import Dict, Optional
import os

class DatabaseManager:
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
    
    def save_practice_session(
        self,
        user_id: str,
        audio_url: str,
        transcription: str,
        word_count: int,
        speaking_rate_wpm: float,
        audio_features: Dict,
        ai_feedback: str,
        score: Optional[float] = None
    ) -> Dict:
        """
        Save a practice session to the database
        
        Args:
            user_id: UUID of the user
            audio_url: URL to the stored audio file
            transcription: What was said
            word_count: Number of words
            speaking_rate_wpm: Speaking rate
            audio_features: Audio analysis data
            ai_feedback: AI-generated feedback
            score: Optional overall score (we can calculate this)
            
        Returns:
            The created session record
        """
        try:
            # Calculate a simple score (0-100) based on metrics
            if score is None:
                score = self._calculate_score(speaking_rate_wpm, audio_features)
            
            # Prepare session data
            session_data = {
                "user_id": user_id,
                "audio_url": audio_url,
                "transcription": transcription,
                "analysis_data": {
                    "word_count": word_count,
                    "speaking_rate_wpm": speaking_rate_wpm,
                    "audio_features": audio_features
                },
                "llm_feedback": ai_feedback,
                "score": score,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Insert into database
            result = self.supabase.table("practice_sessions").insert(session_data).execute()
            
            print(f"Session saved successfully! ID: {result.data[0]['id']}")
            
            # Also update user progress
            self._update_user_progress(user_id, result.data[0]['id'], score, audio_features)
            
            return result.data[0]
            
        except Exception as e:
            print(f"Error saving session: {str(e)}")
            raise
    
    def _calculate_score(self, speaking_rate_wpm: float, audio_features: Dict) -> float:
        """
        Calculate an overall score (0-100) based on speech metrics
        """
        score = 0
        
        # Speaking rate score (40 points max)
        # Ideal range: 120-160 wpm
        if 120 <= speaking_rate_wpm <= 160:
            score += 40
        elif 100 <= speaking_rate_wpm < 120 or 160 < speaking_rate_wpm <= 180:
            score += 30
        elif 80 <= speaking_rate_wpm < 100 or 180 < speaking_rate_wpm <= 200:
            score += 20
        else:
            score += 10
        
        # Volume score (30 points max)
        volume = audio_features.get('average_volume', 0)
        if 0.02 <= volume <= 0.1:
            score += 30
        elif 0.01 <= volume < 0.02 or 0.1 < volume <= 0.15:
            score += 20
        else:
            score += 10
        
        # Consistency score (20 points max)
        # Lower variation = more consistent = better
        volume_var = audio_features.get('volume_variation', 0)
        if volume_var < 0.02:
            score += 20
        elif volume_var < 0.05:
            score += 15
        else:
            score += 10
        
        # Pitch variation score (10 points max)
        # Some variation is good (natural speech)
        pitch_var = audio_features.get('pitch_variation', 0)
        if 30 <= pitch_var <= 80:
            score += 10
        elif 15 <= pitch_var < 30 or 80 < pitch_var <= 100:
            score += 7
        else:
            score += 5
        
        return round(score, 2)
    
    def _update_user_progress(
        self,
        user_id: str,
        session_id: str,
        score: float,
        audio_features: Dict
    ):
        """
        Update user progress tracking
        """
        try:
            progress_data = {
                "user_id": user_id,
                "session_id": session_id,
                "metrics": {
                    "score": score,
                    "volume": audio_features.get('average_volume'),
                    "pitch_variation": audio_features.get('pitch_variation'),
                },
                "created_at": datetime.utcnow().isoformat()
            }
            
            self.supabase.table("user_progress").insert(progress_data).execute()
            
        except Exception as e:
            print(f"Warning: Could not update user progress: {str(e)}")
    
    def get_user_sessions(self, user_id: str, limit: int = 10) -> list:
        """
        Get recent sessions for a user
        
        Args:
            user_id: UUID of the user
            limit: Number of sessions to retrieve
            
        Returns:
            List of session records
        """
        try:
            result = self.supabase.table("practice_sessions")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data
            
        except Exception as e:
            print(f"Error fetching sessions: {str(e)}")
            return []
    
    def get_user_stats(self, user_id: str) -> Dict:
        """
        Get overall statistics for a user
        
        Args:
            user_id: UUID of the user
            
        Returns:
            Dictionary with user statistics
        """
        try:
            sessions = self.get_user_sessions(user_id, limit=100)
            
            if not sessions:
                return {
                    "total_sessions": 0,
                    "average_score": 0,
                    "total_words": 0,
                    "average_wpm": 0
                }
            
            total_sessions = len(sessions)
            total_score = sum(s.get('score', 0) for s in sessions)
            total_words = sum(s.get('analysis_data', {}).get('word_count', 0) for s in sessions)
            total_wpm = sum(s.get('analysis_data', {}).get('speaking_rate_wpm', 0) for s in sessions)
            
            return {
                "total_sessions": total_sessions,
                "average_score": round(total_score / total_sessions, 2),
                "total_words": total_words,
                "average_wpm": round(total_wpm / total_sessions, 2),
                "latest_session": sessions[0].get('created_at') if sessions else None
            }
            
        except Exception as e:
            print(f"Error calculating stats: {str(e)}")
            return {}
    
    def upload_audio_file(self, user_id: str, file_path: str, filename: str) -> str:
        """
        Upload audio file to Supabase Storage
        
        Args:
            user_id: UUID of the user
            file_path: Local path to audio file
            filename: Name for the stored file
            
        Returns:
            Public URL of the uploaded file
        """
        try:
            # Create path: user_id/timestamp_filename
            storage_path = f"{user_id}/{datetime.utcnow().timestamp()}_{filename}"
            
            # Read file
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Upload to Supabase Storage
            self.supabase.storage.from_("audio-recordings").upload(
                storage_path,
                file_data,
                file_options={"content-type": "audio/wav"}
            )
            
            # Get public URL
            public_url = self.supabase.storage.from_("audio-recordings").get_public_url(storage_path)
            
            print(f"Audio uploaded: {public_url}")
            
            return public_url
            
        except Exception as e:
            print(f"Error uploading audio: {str(e)}")
            raise