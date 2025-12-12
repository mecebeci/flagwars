import { createContext, useState, useEffect, useContext } from 'react';
import { jwtDecode } from 'jwt-decode';
import api, { setAuthTokens, clearAuthTokens, getAccessToken } from '../services/api';

// Create the context
const AuthContext = createContext(null);

// Provider component
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Initialize: Check if user is already logged in (on page load/refresh)
  useEffect(() => {
    const initializeAuth = () => {
      const token = getAccessToken();
      
      if (token) {
        try {
          // Decode JWT to get user info
          const decoded = jwtDecode(token);
          
          // Check if token is expired
          const currentTime = Date.now() / 1000;
          if (decoded.exp < currentTime) {
            // Token expired, clear it
            clearAuthTokens();
            setUser(null);
          } else {
            // Token valid, set user
            setUser({
              id: decoded.user_id,
              email: decoded.email,
              username: decoded.username,
            });
          }
        } catch (error) {
          console.error('Invalid token:', error);
          clearAuthTokens();
          setUser(null);
        }
      }
      
      setLoading(false);
    };

    initializeAuth();
  }, []);

  // Login function
  const login = async (username, password) => {
    try {
      const response = await api.post('/auth/login/', {
        username,
        password,
      });

      const { access, refresh } = response.data;

      // Store tokens
      setAuthTokens(access, refresh);

      // Decode access token to get user info
      const decoded = jwtDecode(access);
      setUser({
        id: decoded.user_id,
        email: decoded.email,
        username: decoded.username,
      });

      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Login failed';
      return { success: false, error: errorMessage };
    }
  };

  // Register function
  const register = async (username, email, password) => {
    try {
      const response = await api.post('/auth/register/', {
        username,
        email,
        password,
      });

      const { access, refresh } = response.data;

      // Store tokens
      setAuthTokens(access, refresh);

      // Decode token and set user
      const decoded = jwtDecode(access);
      setUser({
        id: decoded.user_id,
        email: decoded.email,
        username: decoded.username,
      });

      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Registration failed';
      return { success: false, error: errorMessage };
    }
  };

  // Logout function
  const logout = () => {
    clearAuthTokens();
    setUser(null);
  };

  // Context value
  const value = {
    user,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};