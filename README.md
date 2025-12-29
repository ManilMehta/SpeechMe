# SpeechMe - AI-Powered Speech Therapy Application

An intelligent speech therapy practice platform that uses AI to provide real-time feedback on speech patterns, clarity, and delivery. Built with Next.js, FastAPI, OpenAI Whisper, and Meta's Llama.


## Features

### Core Functionality
- **AI Speech Analysis**: Powered by OpenAI Whisper for accurate transcription
- **Personalized Feedback**: Meta Llama 3.1 provides detailed, actionable speech therapy advice
- **Progress Tracking**: Comprehensive dashboard showing improvement over time
- **Practice Scripts**: Curated scripts across 3 difficulty levels and multiple categories
- **User Authentication**: Secure authentication via Supabase Auth
- **Cloud Storage**: Audio recordings stored securely in Supabase Storage

### Speech Analysis Metrics
- **Transcription Accuracy**: Word-for-word transcription of your speech
- **Speaking Rate**: Words per minute (WPM) calculation
- **Volume Analysis**: Average volume and consistency measurements
- **Pitch Variation**: Voice modulation tracking
- **Overall Score**: Comprehensive 0-100 scoring system
- **Duration Tracking**: Session length monitoring

### Practice Features
- **Practice Scripts**: Organized by difficulty (Beginner, Intermediate, Advanced)
- **Multiple Categories**: 
  - Clarity & Articulation
  - Speaking Pace
  - Volume Control
  - Professional Communication
  - Storytelling
  - Technical Speaking
  - Persuasive Speech
- **Random Script Generator**: Get new practice material with one click
- **Difficulty Progression**: Advance from beginner to advanced levels

### User Dashboard
- **Session History**: View all past practice sessions
- **Progress Charts**: Visual representation of score improvement
- **Statistics Overview**: Total sessions, average score, words spoken, and pace
- **Session Details**: Review transcriptions, audio, and AI feedback for any session
- **Audio Playback**: Listen to your recordings anytime

## Tech Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Authentication**: Supabase Auth
- **Deployment**: Vercel

### Backend
- **Framework**: FastAPI (Python)
- **Speech Recognition**: OpenAI Whisper (base model)
- **AI Feedback**: Meta Llama 3.1-8B (via Together AI)
- **Audio Processing**: librosa, soundfile
- **Authentication**: JWT (Supabase tokens)
- **Deployment**: Railway

### Database & Storage
- **Database**: Supabase (PostgreSQL)
- **File Storage**: Supabase Storage
- **Authentication**: Supabase Auth

### AI Services
- **Speech-to-Text**: OpenAI Whisper (self-hosted)
- **LLM**: Together AI (Llama 3.1-8B-Instruct-Turbo)


## Getting Started

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.10+
- **Git**
- **Supabase Account** (free tier)
- **Together AI Account** (free tier with $5 credit)

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/speech-therapy-app.git
cd speech-therapy-app
```

### 2. Set Up Supabase

1. Create a new project at [supabase.com](https://supabase.com)
2. Go to **SQL Editor** and run:
```sql
-- Create profiles table
CREATE TABLE profiles (
  id UUID REFERENCES auth.users PRIMARY KEY,
  email TEXT,
  full_name TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create practice sessions table
CREATE TABLE practice_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES profiles(id),
  audio_url TEXT,
  transcription TEXT,
  analysis_data JSONB,
  llm_feedback TEXT,
  score FLOAT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create progress tracking table
CREATE TABLE user_progress (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES profiles(id),
  session_id UUID REFERENCES practice_sessions(id),
  metrics JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE practice_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_progress ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view own profile" ON profiles
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON profiles
  FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own sessions" ON practice_sessions
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view own sessions" ON practice_sessions
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own progress" ON user_progress
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view own progress" ON user_progress
  FOR SELECT USING (auth.uid() = user_id);

-- Auto-create profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.profiles (id, email, full_name)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', '')
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
```

3. Create Storage Bucket:
   - Go to **Storage** → **New bucket**
   - Name: `audio-recordings`
   - Make it **Public**

4. Get your credentials:
   - Go to **Project Settings** → **API**
   - Copy: **Project URL**, **anon public key**, **service_role key**

### 3. Set Up Backend
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
touch .env
```

Add to `backend/.env`:
```bash
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_role_key
HUGGINGFACE_TOKEN=your_huggingface_token  # Optional, for future use
TOGETHER_API_KEY=your_together_ai_api_key
```

**Get Together AI API Key:**
1. Sign up at [together.ai](https://together.ai)
2. Go to API Keys → Create new key
3. You get $5 free credit
```bash
# Run the backend
python main.py
```

Backend will run on `http://localhost:8000`

### 4. Set Up Frontend
```bash
cd ../frontend

# Install dependencies
npm install

# Create .env.local file
touch .env.local
```

Add to `frontend/.env.local`:
```bash
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_API_URL=http://localhost:8000
```
```bash
# Run the frontend
npm run dev
```

Frontend will run on `http://localhost:3000`

### 5. Test the Application

1. Open `http://localhost:3000`
2. Click **Sign Up** and create an account
3. Select a difficulty level and practice script
4. Click **Start Recording** and read the script
5. Click **Stop Recording**
6. Click **Analyze Speech**
7. View your results and AI feedback!
8. Check the **Dashboard** to see your progress


## Future Enhancements

### Planned Features
- [ ] Voice comparison with ideal speech patterns
- [ ] Real-time feedback during recording
- [ ] Phoneme-level analysis
- [ ] Custom script uploads
- [ ] Therapist dashboard
- [ ] Mobile app (React Native)
- [ ] Offline mode
- [ ] Multi-language support
- [ ] Export progress reports (PDF)
- [ ] Integration with calendar for scheduled practice
- [ ] Gamification (achievements, streaks)

### Model Improvements
- [ ] Fine-tune Llama on speech therapy data
- [ ] Train custom Whisper model for speech disorders
- [ ] Add emotion detection
- [ ] Accent analysis and modification

