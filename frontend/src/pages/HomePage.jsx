import { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import api from '../services/api';

const HomePage = () => {
  const [country, setCountry] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Fetch a random country on component mount
  useEffect(() => {
    fetchRandomCountry();
  }, []);

  const fetchRandomCountry = async () => {
    try {
      setLoading(true);
      const response = await api.get('/game/random-country/');
      setCountry(response.data);
      setError('');
    } catch (err) {
      setError('Failed to load country data');
      console.error('Error fetching country:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleNewFlag = () => {
    fetchRandomCountry();
  };

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-green-400 to-blue-500 py-6">
        <div className="max-w-3xl mx-auto px-4">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold text-center mb-4 text-gray-800">
              🌍 Random Flag Test
            </h2>

            {/* Loading State */}
            {loading && (
              <div className="text-center py-12">
                <div className="text-xl text-gray-600">Loading flag...</div>
              </div>
            )}

            {/* Error State */}
            {error && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
                {error}
              </div>
            )}

            {/* Country Display */}
            {!loading && country && (
              <div className="space-y-6">
                {/* Flag Image - FIXED HEIGHT CONTAINER */}
                <div className="flex justify-center">
                  <div className="w-full max-w-md h-64 flex items-center justify-center">
                    <img
                      src={country.flag_image_url}
                      alt={`Flag of ${country.name}`}
                      className="max-w-full max-h-full object-contain rounded-lg shadow-lg"
                      onError={(e) => {
                        e.target.src = 'https://via.placeholder.com/400x300?text=Flag+Not+Found';
                      }}
                    />
                  </div>
                </div>

                {/* Country Info */}
                <div className="text-center space-y-1">
                  <h3 className="text-xl font-bold text-gray-800">{country.name}</h3>
                  <p className="text-sm text-gray-600">Code: {country.code}</p>
                  {country.region && <p className="text-gray-600">Region: {country.region}</p>}
                </div>

                {/* Get New Flag Button */}
                <div className="text-center">
                  <button
                    onClick={handleNewFlag}
                    disabled={loading}
                    className="bg-blue-600 text-white px-5 py-2 rounded-lg font-semibold text-sm hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    🎲 Get Another Random Flag
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default HomePage;