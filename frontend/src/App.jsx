import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import HomePage from './pages/HomePage';
import QuizPage from './pages/QuizPage';

function App() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        {/* Public Routes */}
        <Route 
          path="/login" 
          element={isAuthenticated ? <Navigate to="/home" replace /> : <LoginPage />} 
        />

        {/* Protected Routes */}
        <Route
          path="/home"
          element={<ProtectedRoute><HomePage /></ProtectedRoute>}
        />
        
        <Route
          path="/challenge"
          element={<ProtectedRoute><QuizPage /></ProtectedRoute>} 
        />

        {/* Default redirect */}
        <Route 
          path="/" 
          element={<Navigate to={isAuthenticated ? "/home" : "/login"} replace />} 
        />

        {/* 404 Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
}

export default App;
