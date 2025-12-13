const QuizStats = ({ 
  score, 
  skipsRemaining, 
  countriesViewed, 
  totalCountries = 192,
  elapsedSeconds = 0  // ⏱️ NEW prop
}) => {
  const progressPercentage = Math.round((countriesViewed / totalCountries) * 100);
  
  // ⏱️ Format seconds to MM:SS
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-4 mb-4">
      <div className="grid grid-cols-4 gap-4 text-center mb-3">  {/* ⏱️ Changed to 4 columns */}
        {/* Score */}
        <div>
          <p className="text-xs text-gray-600 font-semibold uppercase mb-1">
            Score
          </p>
          <p className="text-2xl font-bold text-green-600">
            {score}
          </p>
        </div>

        {/* ⏱️ NEW: Time */}
        <div>
          <p className="text-xs text-gray-600 font-semibold uppercase mb-1">
            Time
          </p>
          <p className="text-2xl font-bold text-blue-600">
            {formatTime(elapsedSeconds)}
          </p>
        </div>

        {/* Skips Remaining */}
        <div>
          <p className="text-xs text-gray-600 font-semibold uppercase mb-1">
            Skips Left
          </p>
          <p className="text-2xl font-bold text-orange-600">
            {skipsRemaining}
          </p>
        </div>

        {/* Progress */}
        <div>
          <p className="text-xs text-gray-600 font-semibold uppercase mb-1">
            Progress
          </p>
          <p className="text-2xl font-bold text-purple-600">
            {countriesViewed}/{totalCountries}
          </p>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div 
          className="bg-purple-600 h-2 rounded-full transition-all duration-300"
          style={{ width: `${progressPercentage}%` }}
        ></div>
      </div>
    </div>
  );
};

export default QuizStats;