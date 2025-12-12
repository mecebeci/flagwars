import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Layout from '../components/Layout';
import api from '../services/api';

const HomePage = () => {
  const { user } = useAuth();

  // If authenticated, show the random flag feature
  if (user) {
    return <AuthenticatedHome />;
  }

  // If not authenticated, show landing page
  return <LandingPage />;
};

// Landing Page for Unauthenticated Users
// Landing Page for Unauthenticated Users
const LandingPage = () => {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="max-w-4xl mx-auto px-4 py-12 text-center">
        {/* Hero Section */}
        <div className="bg-white rounded-lg shadow-lg p-12">
          <h1 className="text-5xl font-bold text-gray-800 mb-4">
            Flag Wars
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Test your knowledge of world flags in this interactive trivia game
          </p>
          
          {/* CTA Buttons - Highlights removed, margin top adjusted slightly if needed */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mt-8">
            <Link
              to="/register"
              className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold text-lg hover:bg-blue-700 transition"
            >
              Get Started
            </Link>
            <Link
              to="/login"
              className="bg-gray-200 text-gray-800 px-8 py-3 rounded-lg font-semibold text-lg hover:bg-gray-300 transition"
            >
              Log In
            </Link>
          </div>
        </div>

        {/* Additional Info */}
        <p className="text-gray-500 mt-8">
          Free to play • Start learning today
        </p>
      </div>
    </div>
  );
};

// Authenticated User Home (Random Flag Feature)
const AuthenticatedHome = () => {
  const [country, setCountry] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

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
      <div className="min-h-screen bg-gray-100 py-6">
        <div className="max-w-3xl mx-auto px-4">
          <div className="bg-white rounded-lg shadow-lg p-6">
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