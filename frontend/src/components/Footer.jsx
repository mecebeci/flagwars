const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-800 text-white py-8 mt-auto">
      <div className="max-w-7xl mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* About Section */}
          <div>
            <h3 className="text-lg font-bold mb-3">Flag Wars</h3>
            <p className="text-gray-400 text-sm">
              Test your knowledge of world flags in this exciting trivia game!
              Challenge yourself and compete on the leaderboard.
            </p>
          </div>
        </div>

        {/* Copyright */}
        <div className="border-t border-gray-700 mt-8 pt-6 text-center text-sm text-gray-400">
          <p>© {currentYear} Flag Wars</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;