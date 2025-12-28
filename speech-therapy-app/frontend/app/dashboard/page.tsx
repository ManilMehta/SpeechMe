'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabase';
import Link from 'next/link';

interface Session {
  id: string;
  created_at: string;
  transcription: string;
  score: number;
  analysis_data: {
    word_count: number;
    speaking_rate_wpm: number;
  };
  llm_feedback: string;
  audio_url: string;
}

interface Stats {
  total_sessions: number;
  average_score: number;
  total_words: number;
  average_wpm: number;
  latest_session: string;
}

export default function DashboardPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedSession, setSelectedSession] = useState<Session | null>(null);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    }
  }, [user, authLoading, router]);

  useEffect(() => {
    if (user) {
      fetchDashboardData();
    }
  }, [user]);

  const fetchDashboardData = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session) return;

      // Fetch sessions
      const sessionsResponse = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/sessions?limit=20`,
        {
          headers: {
            'Authorization': `Bearer ${session.access_token}`,
          },
        }
      );

      if (sessionsResponse.ok) {
        const sessionsData = await sessionsResponse.json();
        setSessions(sessionsData.sessions);
      }

      // Fetch stats
      const statsResponse = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/stats`,
        {
          headers: {
            'Authorization': `Bearer ${session.access_token}`,
          },
        }
      );

      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStats(statsData.stats);
      }

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h1 className="text-4xl font-bold text-gray-800">
              Your Progress Dashboard
            </h1>
            <Link
              href="/"
              className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-6 rounded-lg transition-colors duration-200"
            >
              New Practice Session
            </Link>
          </div>
          <p className="text-gray-600">
            Track your improvement and review past sessions
          </p>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <StatCard
              title="Total Sessions"
              value={stats.total_sessions}
              icon="📊"
            />
            <StatCard
              title="Average Score"
              value={`${stats.average_score}/100`}
              icon="⭐"
            />
            <StatCard
              title="Total Words"
              value={stats.total_words.toLocaleString()}
              icon="💬"
            />
            <StatCard
              title="Average Pace"
              value={`${stats.average_wpm} wpm`}
              icon="⚡"
            />
          </div>
        )}

        {/* Score Chart */}
        {sessions.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">
              Score Progress
            </h2>
            <ScoreChart sessions={sessions} />
          </div>
        )}

        {/* Sessions List */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">
            Recent Sessions
          </h2>
          
          {sessions.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500 text-lg mb-4">
                No practice sessions yet
              </p>
              <Link
                href="/"
                className="text-blue-500 hover:text-blue-600 font-semibold"
              >
                Start your first session →
              </Link>
            </div>
          ) : (
            <div className="space-y-4">
              {sessions.map((session) => (
                <SessionCard
                  key={session.id}
                  session={session}
                  onClick={() => setSelectedSession(session)}
                />
              ))}
            </div>
          )}
        </div>

        {/* Session Detail Modal */}
        {selectedSession && (
          <SessionDetailModal
            session={selectedSession}
            onClose={() => setSelectedSession(null)}
          />
        )}
      </div>
    </div>
  );
}

// Stat Card Component
function StatCard({ title, value, icon }: { title: string; value: string | number; icon: string }) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-medium text-gray-600">{title}</h3>
        <span className="text-2xl">{icon}</span>
      </div>
      <p className="text-3xl font-bold text-gray-800">{value}</p>
    </div>
  );
}

// Session Card Component
function SessionCard({ session, onClick }: { session: Session; onClick: () => void }) {
  const date = new Date(session.created_at);
  const formattedDate = date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <button
      onClick={onClick}
      className="w-full bg-gray-50 hover:bg-gray-100 rounded-lg p-4 text-left transition-colors duration-200"
    >
      <div className="flex justify-between items-start mb-2">
        <div className="flex-1">
          <p className="text-sm text-gray-500 mb-1">{formattedDate}</p>
          <p className="text-gray-800 line-clamp-2">
            "{session.transcription}"
          </p>
        </div>
        <div className="ml-4 text-right">
          <div className={`text-2xl font-bold ${
            session.score >= 80 ? 'text-green-600' :
            session.score >= 60 ? 'text-yellow-600' :
            'text-red-600'
          }`}>
            {session.score}
          </div>
          <p className="text-xs text-gray-500">score</p>
        </div>
      </div>
      <div className="flex gap-4 text-sm text-gray-600">
        <span>📝 {session.analysis_data.word_count} words</span>
        <span>⚡ {session.analysis_data.speaking_rate_wpm.toFixed(0)} wpm</span>
      </div>
    </button>
  );
}

// Score Chart Component
function ScoreChart({ sessions }: { sessions: Session[] }) {
  // Reverse to show oldest to newest
  const chartSessions = [...sessions].reverse().slice(-10);
  
  const maxScore = 100;
  const chartHeight = 200;

  return (
    <div className="relative">
      {/* Y-axis labels */}
      <div className="absolute left-0 top-0 bottom-0 w-8 flex flex-col justify-between text-xs text-gray-500">
        <span>100</span>
        <span>75</span>
        <span>50</span>
        <span>25</span>
        <span>0</span>
      </div>

      {/* Chart area */}
      <div className="ml-12 relative" style={{ height: chartHeight }}>
        {/* Grid lines */}
        <div className="absolute inset-0 flex flex-col justify-between">
          {[0, 1, 2, 3, 4].map((i) => (
            <div key={i} className="border-t border-gray-200" />
          ))}
        </div>

        {/* Bars */}
        <div className="absolute inset-0 flex items-end justify-around px-2">
          {chartSessions.map((session, index) => {
            const height = (session.score / maxScore) * chartHeight;
            const color = session.score >= 80 ? 'bg-green-500' :
                         session.score >= 60 ? 'bg-yellow-500' :
                         'bg-red-500';
            
            return (
              <div key={session.id} className="flex-1 flex flex-col items-center mx-1">
                <div className="w-full flex justify-center">
                  <div
                    className={`w-full max-w-12 ${color} rounded-t transition-all duration-300 hover:opacity-80`}
                    style={{ height: `${height}px` }}
                  />
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  {index + 1}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

// Session Detail Modal
function SessionDetailModal({ session, onClose }: { session: Session; onClose: () => void }) {
  const date = new Date(session.created_at);
  const formattedDate = date.toLocaleDateString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          {/* Header */}
          <div className="flex justify-between items-start mb-4">
            <div>
              <h2 className="text-2xl font-bold text-gray-800 mb-1">
                Session Details
              </h2>
              <p className="text-sm text-gray-500">{formattedDate}</p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-2xl"
            >
              ×
            </button>
          </div>

          {/* Score */}
          <div className="bg-blue-50 rounded-lg p-4 mb-4">
            <div className="flex items-center justify-between">
              <span className="text-lg font-semibold text-gray-700">Overall Score</span>
              <span className={`text-4xl font-bold ${
                session.score >= 80 ? 'text-green-600' :
                session.score >= 60 ? 'text-yellow-600' :
                'text-red-600'
              }`}>
                {session.score}/100
              </span>
            </div>
          </div>

          {/* Transcription */}
          <div className="mb-4">
            <h3 className="font-semibold text-gray-800 mb-2">📝 Transcription</h3>
            <p className="text-gray-700 bg-gray-50 rounded p-4">
              "{session.transcription}"
            </p>
          </div>

          {/* Metrics */}
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="bg-gray-50 rounded p-3">
              <p className="text-sm text-gray-600">Words Spoken</p>
              <p className="text-2xl font-bold text-gray-800">
                {session.analysis_data.word_count}
              </p>
            </div>
            <div className="bg-gray-50 rounded p-3">
              <p className="text-sm text-gray-600">Speaking Rate</p>
              <p className="text-2xl font-bold text-gray-800">
                {session.analysis_data.speaking_rate_wpm.toFixed(0)} wpm
              </p>
            </div>
          </div>

          {/* AI Feedback */}
          <div className="mb-4">
            <h3 className="font-semibold text-gray-800 mb-2">🤖 AI Feedback</h3>
            <div className="text-gray-700 bg-gray-50 rounded p-4 whitespace-pre-wrap">
              {session.llm_feedback}
            </div>
          </div>

          {/* Audio Player */}
          <div className="mb-4">
            <h3 className="font-semibold text-gray-800 mb-2">🎤 Recording</h3>
            <audio controls src={session.audio_url} className="w-full">
              Your browser does not support the audio element.
            </audio>
          </div>

          {/* Close Button */}
          <button
            onClick={onClose}
            className="w-full bg-blue-500 hover:bg-blue-600 text-white font-semibold py-3 rounded-lg transition-colors duration-200"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}