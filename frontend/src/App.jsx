import { Routes, Route, Navigate} from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import HomePage from './pages/HomePage';
import QuizPage from './pages/QuizPage';

function App() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        {/* Public Routes - Redirect to home if already authenticated */}
        <Route 
          path="/login" 
          element={isAuthenticated ? <Navigate to="/" replace /> : <LoginPage />} 
        />
        <Route 
          path="/register" 
          element={isAuthenticated ? <Navigate to="/" replace /> : <RegisterPage />} 
        />

        {/* Home Page - Shows landing page OR authenticated home based on auth status */}
        <Route path="/" element={<HomePage />} />

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