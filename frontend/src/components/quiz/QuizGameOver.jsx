const QuizGameOver = ({ 
  score, 
  countriesViewed, 
  totalCountries = 194, 
  elapsedSeconds = 0,  // ⏱️ NEW prop
  onRestart 
}) => {
  const isAllCompleted = countriesViewed >= totalCountries;

  // ⏱️ Format seconds to MM:SS
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Determine performance level
  let performanceText = 'Great Job!';
  let performanceColor = 'text-green-600';

  if (isAllCompleted) {
    performanceText = 'Perfect! All Flags Completed!';
    performanceColor = 'text-yellow-600';
  } else if (score <= 50) {
    performanceText = 'Keep Practicing!';
    performanceColor = 'text-orange-600';
  } else if (score >= 100) {
    performanceText = 'Excellent!';
    performanceColor = 'text-blue-600';
  }

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="bg-white rounded-xl shadow-lg p-6 text-center">
        {/* Title */}
        <h1 className={`text-3xl font-bold mb-2 ${performanceColor}`}>
          {performanceText}
        </h1>
        <p className="text-base text-gray-600 mb-6">
          Challenge Complete!
        </p>

        {/* Completion Badge */}
        {isAllCompleted && (
          <div className="bg-yellow-100 border-2 border-yellow-500 rounded-lg p-4 mb-6">
            <p className="text-lg font-bold text-yellow-800">
              You've seen all {totalCountries} flags in the world!
            </p>
          </div>
        )}

        {/* Score Display */}
        <div className="bg-slate-800 rounded-xl p-8 mb-6 text-white">
          <p className="text-lg font-semibold mb-3 opacity-90">
            Final Score
          </p>
          <p className="text-6xl font-bold mb-3">
            {score}
          </p>
          <p className="text-lg opacity-90">
            correct answers
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4 mb-6">
          <div className="bg-blue-50 rounded-lg p-3 sm:p-4 text-center">
            <p className="text-[10px] sm:text-xs text-blue-600 font-semibold uppercase mb-1">
              Flags Viewed
            </p>
            <p className="text-xl sm:text-2xl font-bold text-blue-700">
              {countriesViewed}/{totalCountries}
            </p>
          </div>


          {/* ⏱️ NEW: Time Taken */}
          <div className="bg-indigo-50 rounded-lg p-4">
            <p className="text-xs text-indigo-600 font-semibold uppercase mb-1">
              Time
            </p>
            <p className="text-2xl font-bold text-indigo-700">
              {formatTime(elapsedSeconds)}
            </p>
          </div>

          <div className="bg-green-50 rounded-lg p-4">
            <p className="text-xs text-green-600 font-semibold uppercase mb-1">
              Accuracy
            </p>
            <p className="text-2xl font-bold text-green-700">
              {countriesViewed > 0 ? ((score / countriesViewed) * 100).toFixed(1) : 0}%
            </p>
          </div>

          <div className="bg-purple-50 rounded-lg p-4">
            <p className="text-xs text-purple-600 font-semibold uppercase mb-1">
              Completion
            </p>
            <p className="text-2xl font-bold text-purple-700">
              {((countriesViewed / totalCountries) * 100).toFixed(1)}%
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="space-y-3">
          <button
            onClick={onRestart}
            className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold text-base hover:bg-blue-700 transition shadow-lg"
          >
            Play Again
          </button>
          <button
            onClick={() => window.location.href = '/leaderboard'}
            className="w-full bg-purple-600 text-white px-6 py-3 rounded-lg font-semibold text-base hover:bg-purple-700 transition shadow-lg"
          >
            View Leaderboard
          </button>
          <button
            onClick={() => window.location.href = '/home'}
            className="w-full bg-gray-200 text-gray-700 px-6 py-3 rounded-lg font-semibold text-base hover:bg-gray-300 transition shadow-lg"
          >
            Back to Home
          </button>
        </div>
      </div>
    </div>
  );
};

export default QuizGameOver;
