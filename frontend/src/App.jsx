import { Routes, Route, Navigate} from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import HomePage from './pages/HomePage';
import QuizPage from './pages/QuizPage';
import LeaderboardPage from './pages/LeaderboardPage';
import ProfilePage from './pages/ProfilePage';

function App() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        {/* Public Routes - No automatic redirect, let pages handle it */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Home Page - Shows landing page OR authenticated home based on auth status */}
        <Route path="/" element={<HomePage />} />

        {/* Leaderboard */}
        <Route path="/leaderboard" element={<LeaderboardPage />} />

        {/* Profile page */}
        <Route path="/profile" element={<ProfilePage />} />

        {/* Protected Routes */}
        <Route
          path="/challenge"
          element={<ProtectedRoute><QuizPage /></ProtectedRoute>} 
        />

        {/* 404 Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
}

export default App;