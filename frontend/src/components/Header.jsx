import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import logo from '../assets/flag-wars-logo.png';

const Header = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleNavClick = (path) => {
    navigate(path);
    setMobileMenuOpen(false); // Close menu after navigation
  };

  return (
    <header className="bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          {/* Logo */}
          <div 
            onClick={() => navigate('/home')} 
            className="flex items-center gap-3 cursor-pointer"
          >
            <img 
              src={logo} 
              alt="Flag Wars" 
              className="h-10 w-auto object-contain"  
            />
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-6">
            <button
              onClick={() => navigate('/home')}
              className="text-gray-700 hover:text-blue-600 font-medium transition"
            >
              Home
            </button>
            <button
              onClick={() => navigate('/challenge')}
              className="text-gray-700 hover:text-blue-600 font-medium transition"
            >
              Challenge
            </button>
            <button
              onClick={() => navigate('/leaderboard')}
              className="text-gray-700 hover:text-blue-600 font-medium transition"
            >
              Leaderboard
            </button>
            <button
              onClick={() => navigate('/profile')}
              className="text-gray-700 hover:text-blue-600 font-medium transition"
            >
              Profile
            </button>
          </nav>

          {/* Desktop: User Info + Logout */}
          <div className="hidden md:flex items-center gap-4">
            <span className="text-gray-700">
              Welcome, <strong>{user?.username || 'Guest'}</strong>!
            </span>
            <button
              onClick={handleLogout}
              className="border border-red-500 text-red-500 bg-transparent hover:bg-red-50 px-4 py-2 rounded-lg transition font-medium"
            >
              Logout
            </button>
          </div>

          {/* Mobile: Hamburger Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden text-gray-700 focus:outline-none"
            aria-label="Toggle menu"
          >
            <svg 
              className="w-6 h-6" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              {mobileMenuOpen ? (
                // X icon when menu is open
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M6 18L18 6M6 6l12 12" 
                />
              ) : (
                // Hamburger icon when menu is closed
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M4 6h16M4 12h16M4 18h16" 
                />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile Menu Dropdown */}
        {mobileMenuOpen && (
          <nav className="md:hidden mt-4 pb-4 border-t border-gray-200">
            <div className="flex flex-col gap-3 pt-4">
              {/* User greeting */}
              <div className="text-gray-700 font-medium px-2 pb-2 border-b border-gray-200">
                Welcome, <strong>{user?.username || 'Guest'}</strong>!
              </div>

              {/* Navigation links */}
              <button
                onClick={() => handleNavClick('/home')}
                className="text-left text-gray-700 hover:text-blue-600 hover:bg-gray-50 px-2 py-2 rounded transition"
              >
                Home
              </button>
              <button
                onClick={() => handleNavClick('/challenge')}
                className="text-left text-gray-700 hover:text-blue-600 hover:bg-gray-50 px-2 py-2 rounded transition"
              >
                Challenge
              </button>
              <button
                onClick={() => handleNavClick('/leaderboard')}
                className="text-left text-gray-700 hover:text-blue-600 hover:bg-gray-50 px-2 py-2 rounded transition"
              >
                Leaderboard
              </button>
              <button
                onClick={() => handleNavClick('/profile')}
                className="text-left text-gray-700 hover:text-blue-600 hover:bg-gray-50 px-2 py-2 rounded transition"
              >
                Profile
              </button>

              {/* Logout button */}
              <button
                onClick={handleLogout}
                className="border border-red-500 text-red-500 bg-transparent hover:bg-red-50 px-4 py-2 rounded-lg transition font-medium mt-2"
              >
                Logout
              </button>
            </div>
          </nav>
        )}
      </div>
    </header>
  );
};

export default Header;