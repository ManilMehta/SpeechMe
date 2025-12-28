import whisper
import torch
import librosa
import numpy as np
from pathlib import Path
import soundfile as sf

class AudioProcessor:
    def __init__(self):
        """Initialize Whisper model for transcription"""
        print("Loading Whisper model...")
        # Using 'base' model - good balance of speed and accuracy
        # Options: tiny, base, small, medium, large
        self.model = whisper.load_model("base")
        print("Whisper model loaded successfully!")
        
    def transcribe_audio(self, audio_path: str) -> dict:
        """
        Transcribe audio file using Whisper
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            dict with transcription and metadata
        """
        try:
            print(f"Transcribing audio: {audio_path}")
            
            # Transcribe with Whisper
            result = self.model.transcribe(
                audio_path,
                language="en",  # Force English
                task="transcribe"
            )
            
            transcription = result["text"].strip()
            segments = result.get("segments", [])
            
            print(f"Transcription complete: {transcription[:100]}...")
            
            return {
                "transcription": transcription,
                "segments": segments,
                "language": result.get("language", "en")
            }
            
        except Exception as e:
            print(f"Error in transcription: {str(e)}")
            raise
    
    def analyze_audio_features(self, audio_path: str) -> dict:
        """
        Extract audio features for speech analysis
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            dict with audio features
        """
        try:
            print(f"Analyzing audio features: {audio_path}")
            
            # Load audio file
            audio, sr = librosa.load(audio_path, sr=16000)
            
            # Calculate various features
            
            # 1. Speaking rate (words per minute estimate)
            duration = librosa.get_duration(y=audio, sr=sr)
            
            # 2. Volume/Energy
            rms = librosa.feature.rms(y=audio)[0]
            avg_volume = float(np.mean(rms))
            volume_std = float(np.std(rms))
            
            # 3. Pitch analysis
            pitches, magnitudes = librosa.piptrack(y=audio, sr=sr)
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            avg_pitch = float(np.mean(pitch_values)) if pitch_values else 0
            pitch_variation = float(np.std(pitch_values)) if pitch_values else 0
            
            # 4. Speech pace (zero crossing rate - indicates speech vs silence)
            zcr = librosa.feature.zero_crossing_rate(audio)[0]
            avg_zcr = float(np.mean(zcr))
            
            # 5. Pauses detection (simple silence detection)
            silence_threshold = 0.01
            is_silent = rms < silence_threshold
            silence_ratio = float(np.sum(is_silent) / len(is_silent))
            
            features = {
                "duration_seconds": float(duration),
                "average_volume": avg_volume,
                "volume_variation": volume_std,
                "average_pitch_hz": avg_pitch,
                "pitch_variation": pitch_variation,
                "speech_rate": avg_zcr,
                "silence_ratio": silence_ratio,
                "sample_rate": sr
            }
            
            print("Audio features extracted successfully!")
            return features
            
        except Exception as e:
            print(f"Error analyzing audio features: {str(e)}")
            raise
    
    def process_audio(self, audio_path: str) -> dict:
        """
        Complete audio processing pipeline
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            dict with transcription and features
        """
        # Get transcription
        transcription_result = self.transcribe_audio(audio_path)
        
        # Get audio features
        features = self.analyze_audio_features(audio_path)
        
        # Combine results
        result = {
            "transcription": transcription_result["transcription"],
            "word_count": len(transcription_result["transcription"].split()),
            "segments": transcription_result["segments"],
            "audio_features": features,
            "speaking_rate_wpm": None
        }
        
        # Calculate speaking rate (words per minute)
        if features["duration_seconds"] > 0:
            result["speaking_rate_wpm"] = (
                result["word_count"] / features["duration_seconds"]
            ) * 60
        
        return result