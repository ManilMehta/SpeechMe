'use client';

import { useState, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { supabase } from '@/lib/supabase';

export default function AudioRecorder() {
  const { user } = useAuth(); 
  const [isRecording, setIsRecording] = useState(false);
  const [audioURL, setAudioURL] = useState<string>('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [feedback, setFeedback] = useState<string>('');
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const startRecording = async () => {
    try {
      // Request microphone permission
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Create MediaRecorder instance
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      // Collect audio data
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      // When recording stops, create audio URL
      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        const url = URL.createObjectURL(audioBlob);
        setAudioURL(url);
        
        // Stop all tracks to release microphone
        stream.getTracks().forEach(track => track.stop());
      };

      // Start recording
      mediaRecorder.start();
      setIsRecording(true);
      setFeedback(''); // Clear previous feedback
    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Could not access microphone. Please grant permission.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const analyzeAudio = async () => {
    if (!audioURL) {
      alert('Please record audio first!');
      return;
    }

    if (!user) {
      alert('You must be logged in!');
      return;
    }

    setIsAnalyzing(true);
    setFeedback('');

    try {
      const response = await fetch(audioURL);
      const audioBlob = await response.blob();

      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');

      // Get the auth token from Supabase
      const { data: { session } } = await supabase.auth.getSession();
      
      console.log('Session:', session ? 'EXISTS' : 'NULL');
      console.log('Token preview:', session?.access_token?.substring(0, 30));
      
      if (!session) {
        alert('Session expired. Please log in again.');
        return;
      }

      console.log('Sending request with auth header...');

      const apiResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/analyze-speech`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
        },
        body: formData,
      });

      console.log('Response status:', apiResponse.status);

      if (!apiResponse.ok) {
        const errorText = await apiResponse.text();
        console.error('Error response:', errorText);
        throw new Error('Analysis failed');
      }

      const result = await apiResponse.json();
      
      // Format the feedback with AI insights
      const formattedFeedback = `
📝 TRANSCRIPTION:
"${result.transcription}"

📊 SPEECH METRICS:
- Words spoken: ${result.word_count}
- Speaking rate: ${result.speaking_rate_wpm?.toFixed(1)} words per minute
- Duration: ${result.audio_features.duration_seconds.toFixed(1)} seconds
- Overall Score: ${result.score}/100

🤖 AI SPEECH THERAPIST FEEDBACK:

${result.ai_feedback}
      `.trim();
      
      setFeedback(formattedFeedback);
      
    } catch (error) {
      console.error('Error analyzing audio:', error);
      setFeedback('Error analyzing audio. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const clearRecording = () => {
    setAudioURL('');
    setFeedback('');
    audioChunksRef.current = [];
  };

  return (
    <div className="w-full max-w-2xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">
          Speech Therapy Practice
        </h1>
        <p className="text-gray-600">
          Record your speech and receive personalized feedback
        </p>
      </div>

      {/* Recording Controls */}
      <div className="bg-white rounded-lg shadow-md p-8">
        <div className="flex flex-col items-center space-y-4">
          
          {/* Recording Button */}
          {!isRecording ? (
            <button
              onClick={startRecording}
              className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-4 px-8 rounded-full transition-colors duration-200 flex items-center space-x-2"
            >
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
              </svg>
              <span>Start Recording</span>
            </button>
          ) : (
            <button
              onClick={stopRecording}
              className="bg-red-500 hover:bg-red-600 text-white font-semibold py-4 px-8 rounded-full transition-colors duration-200 flex items-center space-x-2 animate-pulse"
            >
              <div className="w-4 h-4 bg-white rounded-full"></div>
              <span>Stop Recording</span>
            </button>
          )}

          {/* Recording Status */}
          {isRecording && (
            <p className="text-red-500 font-medium">Recording in progress...</p>
          )}
        </div>

        {/* Audio Player */}
        {audioURL && !isRecording && (
          <div className="mt-6 space-y-4">
            <div className="flex justify-center">
              <audio controls src={audioURL} className="w-full max-w-md">
                Your browser does not support the audio element.
              </audio>
            </div>
            
            {/* Action Buttons */}
            <div className="flex justify-center space-x-4">
              <button
                onClick={analyzeAudio}
                disabled={isAnalyzing}
                className="bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white font-semibold py-2 px-6 rounded-lg transition-colors duration-200"
              >
                {isAnalyzing ? 'Analyzing...' : 'Analyze Speech'}
              </button>
              
              <button
                onClick={clearRecording}
                className="bg-gray-500 hover:bg-gray-600 text-white font-semibold py-2 px-6 rounded-lg transition-colors duration-200"
              >
                Record Again
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Feedback Section */}
      {feedback && (
        <div className="bg-blue-50 rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-800 mb-3">
            Analysis & Feedback
          </h2>
          <div className="bg-white rounded p-4 text-gray-700 whitespace-pre-wrap">
            {feedback}
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h3 className="font-semibold text-gray-800 mb-2">How to use:</h3>
        <ol className="list-decimal list-inside space-y-1 text-gray-600">
          <li>Click "Start Recording" and speak clearly into your microphone</li>
          <li>Click "Stop Recording" when you're finished</li>
          <li>Listen to your recording to verify it captured correctly</li>
          <li>Click "Analyze Speech" to receive personalized feedback</li>
          <li>Practice the suggestions and record again to track improvement</li>
        </ol>
      </div>
    </div>
  );
}