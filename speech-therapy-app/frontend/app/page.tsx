'use client';

import AudioRecorder from './components/AudioRecorder';
import { useAuth } from './context/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function Home() {
  const { user, loading, signOut } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login');
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return null; // Will redirect to login
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-blue-50 to-white py-12 px-4">
      {/* Header with user info and logout */}
      <div className="max-w-2xl mx-auto mb-6 flex justify-between items-center">
        <div>
          <p className="text-gray-600">Welcome back,</p>
          <p className="text-xl font-semibold text-gray-800">
            {user.user_metadata?.full_name || user.email}
          </p>
        </div>
        <button
          onClick={signOut}
          className="bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold py-2 px-4 rounded-lg transition-colors duration-200"
        >
          Sign Out
        </button>
      </div>

      <AudioRecorder />
    </main>
  );
}