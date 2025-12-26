import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Layout from '../components/Layout';
import { getLeaderboard } from '../services/api';

const LeaderboardPage = () => {
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchLeaderboard();
  }, []);

  const fetchLeaderboard = async () => {
    try {
      setLoading(true);
      const data = await getLeaderboard();
      setLeaderboard(data.leaderboard || []);
    } catch (err) {
      console.error('Failed to fetch leaderboard:', err);
      setError('Failed to load leaderboard. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
  };

  const getMedalColor = (rank) => {
    switch (rank) {
      case 1:
        return 'bg-yellow-400 text-yellow-900';
      case 2:
        return 'bg-gray-300 text-gray-800';
      case 3:
        return 'bg-orange-400 text-orange-900';
      default:
        return 'bg-blue-100 text-blue-900';
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="min-h-screen bg-gray-100 flex items-center justify-center">
          <p className="text-gray-600">Loading leaderboard...</p>
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <div className="min-h-screen bg-gray-100 flex items-center justify-center">
          <div className="bg-red-100 border border-red-400 text-red-700 px-6 py-4 rounded">
            {error}
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="min-h-screen bg-gray-100 py-8 px-4">
        <div className="max-w-4xl mx-auto">

          {/* Header */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-6 text-center">
            <h1 className="text-3xl font-bold text-gray-800 mb-2">
              Global Leaderboard
            </h1>
            <p className="text-gray-600">
              Top 10 Players – Best Performance
            </p>
          </div>

          {/* Leaderboard Table */}
          {leaderboard.length > 0 && (
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase">
                        Rank
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase">
                        Player
                      </th>
                      <th className="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase">
                        Score
                      </th>
                      <th className="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase">
                        Time
                      </th>
                      <th className="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase">
                        Date
                      </th>
                    </tr>
                  </thead>

                  <tbody className="divide-y divide-gray-200">
                    {leaderboard.map((entry) => (
                      <tr
                        key={entry.id}
                        className="hover:bg-gray-50 transition"
                      >
                        <td className="px-6 py-4">
                          <span
                            className={`inline-flex items-center justify-center w-8 h-8 rounded-full font-bold text-sm ${getMedalColor(
                              entry.rank
                            )}`}
                          >
                            {entry.rank}
                          </span>
                        </td>

                        <td className="px-6 py-4">
                          <div className="font-semibold text-gray-900">
                            {entry.username}
                          </div>
                        </td>

                        <td className="px-6 py-4 text-center">
                          <span className="text-lg font-bold text-green-600">
                            {entry.score}
                          </span>
                        </td>

                        <td className="px-6 py-4 text-center">
                          <span className="font-semibold text-blue-600">
                            {formatTime(entry.time_elapsed_seconds)}
                          </span>
                        </td>

                        <td className="px-6 py-4 text-center text-gray-600">
                          {formatDate(entry.completed_at)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Empty State */}
          {leaderboard.length === 0 && (
            <div className="bg-white rounded-lg shadow-md p-8 text-center">
              <p className="text-gray-600 mb-6">
                No leaderboard entries yet. Be the first to complete a game.
              </p>

              <Link
                to="/challenge"
                className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition"
              >
                Start Playing
              </Link>
            </div>
          )}

          {/* Back Button */}
          <div className="mt-8 text-center">
            <Link
              to="/home"
              className="inline-block bg-gray-200 text-gray-700 px-6 py-3 rounded-lg font-semibold hover:bg-gray-300 transition"
            >
              Back to Home
            </Link>
          </div>

        </div>
      </div>
    </Layout>
  );
};

export default LeaderboardPage;
