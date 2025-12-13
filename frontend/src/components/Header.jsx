import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import logo from '../assets/flag-wars-logo.png';

const Header = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
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
              className="h-10 w-auto mb-2 object-contain"  
            />
          </div>

          {/* Navigation Links */}
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

          {/* User Info + Logout */}
          <div className="flex items-center gap-4">
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
        </div>
      </div>
    </header>
  );
};

export default Header;
