import os
from together import Together
from typing import Dict, List

class SpeechTherapist:
    def __init__(self):
        """Initialize the Llama model for speech therapy feedback"""
        self.client = Together(api_key=os.getenv("TOGETHER_API_KEY"))
        # Using Llama 3.2 - excellent for conversational tasks
        self.model = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
        
        # System prompt that defines the AI's role
        self.system_prompt = """You are an expert speech therapist AI assistant. Your role is to provide constructive, encouraging feedback on speech practice sessions.

Your feedback should:
- Be warm, supportive, and encouraging
- Identify specific strengths in the person's speech
- Suggest 2-3 concrete, actionable improvements
- Provide techniques or exercises for improvement
- Be appropriate for the person's skill level
- Focus on one main area for improvement at a time
- End with encouragement and next steps

Analyze the speech data provided and give personalized feedback."""

    def generate_feedback(
        self, 
        transcription: str,
        audio_features: Dict,
        speaking_rate_wpm: float,
        word_count: int
    ) -> str:
        """
        Generate personalized speech therapy feedback using Llama
        
        Args:
            transcription: What the person said
            audio_features: Technical audio analysis
            speaking_rate_wpm: Speaking rate in words per minute
            word_count: Number of words spoken
            
        Returns:
            Personalized feedback as a string
        """
        
        # Create a detailed prompt with the analysis
        user_prompt = f"""Please analyze this speech practice session and provide feedback:

TRANSCRIPTION:
"{transcription}"

SPEECH METRICS:
- Words spoken: {word_count}
- Speaking rate: {speaking_rate_wpm:.1f} words per minute (ideal: 120-160 wpm)
- Duration: {audio_features['duration_seconds']:.1f} seconds
- Average volume: {audio_features['average_volume']:.3f} (0-1 scale)
- Volume consistency: {audio_features['volume_variation']:.3f}
- Pitch variation: {audio_features['pitch_variation']:.2f} Hz
- Silence ratio: {audio_features['silence_ratio']:.2f} (pauses in speech)

Please provide:
1. What they did well
2. One main area for improvement
3. Specific technique or exercise to practice
4. Encouragement for next session"""

        try:
            # Call Llama via Together AI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,  # Creative but not too random
                max_tokens=500,   # Reasonable length response
            )
            
            feedback = response.choices[0].message.content
            return feedback
            
        except Exception as e:
            print(f"Error generating feedback: {str(e)}")
            return self._generate_fallback_feedback(
                speaking_rate_wpm, 
                audio_features
            )
    
    def _generate_fallback_feedback(
        self, 
        speaking_rate_wpm: float,
        audio_features: Dict
    ) -> str:
        """
        Generate basic feedback if AI call fails
        """
        feedback = "Great job completing this practice session!\n\n"
        
        # Speaking rate feedback
        if speaking_rate_wpm < 120:
            feedback += "Try to speak a bit faster. A comfortable pace is 120-160 words per minute.\n"
        elif speaking_rate_wpm > 160:
            feedback += "Try to slow down slightly. Take time to articulate each word clearly.\n"
        else:
            feedback += "Your speaking pace is excellent!\n"
        
        # Volume feedback
        if audio_features['average_volume'] < 0.02:
            feedback += "Try to project your voice more. Speak louder and with more confidence.\n"
        elif audio_features['average_volume'] > 0.1:
            feedback += "You're speaking quite loudly. Try to moderate your volume.\n"
        else:
            feedback += "Your volume level is great!\n"
        
        feedback += "\nKeep practicing! Consistency is key to improvement."
        
        return feedback
    
    def generate_practice_suggestions(self, session_history: List[Dict]) -> str:
        """
        Analyze multiple sessions and suggest practice areas
        
        Args:
            session_history: List of previous session results
            
        Returns:
            Practice suggestions based on patterns
        """
        if not session_history:
            return "Complete your first session to get personalized suggestions!"
        
        # This will be useful later for tracking progress
        user_prompt = f"""Based on these practice sessions, what should the user focus on?

Session history: {len(session_history)} sessions completed

Recent patterns:
{self._summarize_sessions(session_history)}

Provide 3 specific practice exercises or focus areas."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=400,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating suggestions: {str(e)}")
            return "Keep practicing daily for best results!"
    
    def _summarize_sessions(self, sessions: List[Dict]) -> str:
        """Helper to summarize session data"""
        if not sessions:
            return "No sessions yet"
        
        recent = sessions[-5:]  # Last 5 sessions
        avg_wpm = sum(s.get('speaking_rate_wpm', 0) for s in recent) / len(recent)
        avg_words = sum(s.get('word_count', 0) for s in recent) / len(recent)
        
        return f"Average speaking rate: {avg_wpm:.1f} wpm, Average words per session: {avg_words:.1f}"