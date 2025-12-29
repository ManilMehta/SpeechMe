'use client';

import { useState, useRef, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { supabase } from '@/lib/supabase';

interface PracticeScript {
  text: string;
  difficulty: string;
  category: string;
  word_count: number;
}

export default function AudioRecorder() {
  const { user } = useAuth();
  const [isRecording, setIsRecording] = useState(false);
  const [audioURL, setAudioURL] = useState<string>('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [feedback, setFeedback] = useState<string>('');
  
  // Script state
  const [currentScript, setCurrentScript] = useState<PracticeScript | null>(null);
  const [difficulty, setDifficulty] = useState<string>('beginner');
  const [loadingScript, setLoadingScript] = useState(false);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  // Load initial script
  useEffect(() => {
    loadNewScript();
  }, []);

  const loadNewScript = async () => {
    setLoadingScript(true);
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/practice-script?difficulty=${difficulty}`
      );
      
      if (response.ok) {
        const data = await response.json();
        setCurrentScript(data.script);
      }
    } catch (error) {
      console.error('Error loading script:', error);
    } finally {
      setLoadingScript(false);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        const url = URL.createObjectURL(audioBlob);
        setAudioURL(url);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      setFeedback('');
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

      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session) {
        alert('Session expired. Please log in again.');
        return;
      }

      const apiResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/analyze-speech`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
        },
        body: formData,
      });

      if (!apiResponse.ok) {
        throw new Error('Analysis failed');
      }

      const result = await apiResponse.json();
      
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
    loadNewScript(); // Load a new script for next practice
  };

  return (
    <div className="w-full max-w-2xl mx-auto p-6 space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">
          Speech Therapy Practice
        </h1>
        <p className="text-gray-600">
          Read the script below and record yourself
        </p>
      </div>

      {/* Difficulty Selector */}
      <div className="bg-white rounded-lg shadow-md p-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Difficulty Level
        </label>
        <div className="flex gap-2">
          {['beginner', 'intermediate', 'advanced'].map((level) => (
            <button
              key={level}
              onClick={() => {
                setDifficulty(level);
                setCurrentScript(null);
                setTimeout(() => loadNewScript(), 100);
              }}
              className={`flex-1 py-2 px-4 rounded-lg font-semibold transition-colors ${
                difficulty === level
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {level.charAt(0).toUpperCase() + level.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Practice Script Display */}
      {currentScript && (
        <div className="bg-blue-50 rounded-lg shadow-md p-6">
          <div className="flex justify-between items-start mb-3">
            <div>
              <h2 className="text-lg font-bold text-gray-800">Practice Script</h2>
              <p className="text-sm text-gray-600">
                {currentScript.category} • {currentScript.word_count} words
              </p>
            </div>
            <button
              onClick={loadNewScript}
              disabled={loadingScript}
              className="text-blue-500 hover:text-blue-600 font-semibold text-sm"
            >
              {loadingScript ? '...' : 'New Script'}
            </button>
          </div>
          <p className="text-lg text-gray-800 leading-relaxed">
            {currentScript.text}
          </p>
        </div>
      )}

      {/* Recording Controls */}
      <div className="bg-white rounded-lg shadow-md p-8">
        <div className="flex flex-col items-center space-y-4">
          
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

          {isRecording && (
            <p className="text-red-500 font-medium">Recording in progress...</p>
          )}
        </div>

        {audioURL && !isRecording && (
          <div className="mt-6 space-y-4">
            <div className="flex justify-center">
              <audio controls src={audioURL} className="w-full max-w-md">
                Your browser does not support the audio element.
              </audio>
            </div>
            
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
                Try New Script
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
    </div>
  );
}