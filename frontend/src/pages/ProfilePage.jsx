import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import Layout from '../components/Layout';
import { getUserStats, getRecentGames } from '../services/api';

const ProfilePage = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [recentGames, setRecentGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchProfileData();
  }, []);

  const fetchProfileData = async () => {
    try {
      setLoading(true);
      const [statsData, gamesData] = await Promise.all([
        getUserStats(),
        getRecentGames(),
      ]);
      setStats(statsData);
      setRecentGames(gamesData);
    } catch (err) {
      console.error('Failed to fetch profile data:', err);
      setError('Failed to load profile. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds = 0) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  if (loading) {
    return (
      <Layout>
        <div className="min-h-screen bg-gray-100 py-8 px-4 flex items-center justify-center">
          <p className="text-gray-600">Loading profile...</p>
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <div className="min-h-screen bg-gray-100 py-8 px-4 flex items-center justify-center">
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="min-h-screen bg-gray-100 py-8 px-4">
        <div className="max-w-5xl mx-auto">

          {/* Profile Header */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h1 className="text-3xl font-bold text-gray-800 mb-2">
              {user?.username}'s Profile
            </h1>
            <p className="text-gray-600">
              Member since {formatDate(stats?.member_since)}
            </p>
          </div>

          {/* Statistics */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
            <StatBox title="Best Score" value={stats?.best_score} color="text-green-600" />
            <StatBox title="Best Time" value={formatTime(stats?.best_time)} color="text-blue-600" />
            <StatBox title="Games Played" value={stats?.completed_games} color="text-purple-600" />
            <StatBox title="Avg Score" value={Math.round(stats?.average_score || 0)} color="text-orange-600" />
            <StatBox title="Total Correct" value={stats?.total_correct_answers} color="text-indigo-600" />
          </div>

          {/* Recent Games */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4">
              Recent Games
            </h2>

            {recentGames.length === 0 ? (
              <p className="text-gray-600 text-center py-8">
                No completed games yet.
              </p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b">
                    <tr>
                      <TableHeader>Date</TableHeader>
                      <TableHeader center>Score</TableHeader>
                      <TableHeader center>Time</TableHeader>
                      <TableHeader center>Completion</TableHeader>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {recentGames.map((game) => (
                      <tr key={game.id} className="hover:bg-gray-50">
                        <td className="px-4 py-3 text-sm">
                          {formatDate(game.completed_at)}
                        </td>
                        <td className="px-4 py-3 text-center text-green-600 font-semibold">
                          {game.score}
                        </td>
                        <td className="px-4 py-3 text-center text-blue-600 font-semibold">
                          {formatTime(game.time_elapsed_seconds)}
                        </td>
                        <td className="px-4 py-3 text-center text-gray-600">
                          {game.completion_percentage}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Back Button */}
          <div className="mt-6 text-center">
            <a
              href="/home"
              className="inline-block bg-gray-200 text-gray-700 px-6 py-3 rounded-lg font-semibold hover:bg-gray-300 transition"
            >
              Back to Home
            </a>
          </div>

        </div>
      </div>
    </Layout>
  );
};

const StatBox = ({ title, value, color }) => (
  <div className="bg-white rounded-lg shadow-md p-4 text-center">
    <p className="text-xs text-gray-600 font-semibold uppercase mb-1">
      {title}
    </p>
    <p className={`text-2xl font-bold ${color}`}>
      {value ?? 0}
    </p>
  </div>
);

const TableHeader = ({ children, center }) => (
  <th
    className={`px-4 py-3 text-xs font-semibold text-gray-600 uppercase ${
      center ? 'text-center' : 'text-left'
    }`}
  >
    {children}
  </th>
);

export default ProfilePage;
