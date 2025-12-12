import { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import api from '../services/api';

const HomePage = () => {
  const [country, setCountry] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Fetch a random country on component mount
  useEffect(() => {
    const fetchRandomCountry = async () => {
      try {
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

    fetchRandomCountry();
  }, []);

  const handleNewFlag = async () => {
    setLoading(true);
    try {
      const response = await api.get('/game/random-country/');
      setCountry(response.data);
      setError('');
    } catch (err) {
      setError('Failed to load country data');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="bg-gradient-to-br from-green-400 to-blue-500 min-h-full py-12">
        <div className="max-w-4xl mx-auto px-4">
          <div className="bg-white rounded-lg shadow-2xl p-8">
            <h2 className="text-3xl font-bold text-center mb-8 text-gray-800">
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
                {/* Flag Image */}
                <div className="flex justify-center">
                  <img
                    src={country.flag_image_url}
                    alt={`Flag of ${country.name}`}
                    className="w-full max-w-md rounded-lg shadow-lg border-4 border-gray-200"
                    onError={(e) => {
                      e.target.src = 'https://via.placeholder.com/400x300?text=Flag+Not+Found';
                    }}
                  />
                </div>

                {/* Country Info */}
                <div className="text-center space-y-2">
                  <h3 className="text-2xl font-bold text-gray-800">{country.name}</h3>
                  <p className="text-gray-600">Code: {country.code}</p>
                  <p className="text-gray-600">Region: {country.region || 'N/A'}</p>
                </div>

                {/* Get New Flag Button */}
                <div className="text-center">
                  <button
                    onClick={handleNewFlag}
                    className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition"
                  >
                    Get Another Random Flag
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