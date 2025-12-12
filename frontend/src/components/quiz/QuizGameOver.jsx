const QuizGameOver = ({ score, totalQuestions, onRestart }) => {
  const percentage = Math.round((score / totalQuestions) * 100);
  
  // Determine performance level
  let performanceEmoji = '🎉';
  let performanceText = 'Excellent!';
  let performanceColor = 'text-green-600';
  
  if (percentage < 50) {
    performanceEmoji = '📚';
    performanceText = 'Keep Practicing!';
    performanceColor = 'text-orange-600';
  } else if (percentage < 80) {
    performanceEmoji = '👍';
    performanceText = 'Good Job!';
    performanceColor = 'text-blue-600';
  }

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="bg-white rounded-xl shadow-lg p-6 text-center">
        {/* Performance Emoji */}
        <div className="text-6xl mb-4">{performanceEmoji}</div>
        
        {/* Title */}
        <h1 className={`text-3xl font-bold mb-2 ${performanceColor}`}>
          {performanceText}
        </h1>
        <p className="text-base text-gray-600 mb-6">
          Quiz Complete!
        </p>

        {/* Score Display */}
        <div className="bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl p-8 mb-6 text-white">
          <p className="text-lg font-semibold mb-3 opacity-90">
            Your Score
          </p>
          <p className="text-6xl font-bold mb-3">
            {score}/{totalQuestions}
          </p>
          <p className="text-2xl opacity-90">
            {percentage}% Correct
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-green-50 rounded-lg p-4">
            <p className="text-xs text-green-600 font-semibold uppercase mb-1">
              Correct
            </p>
            <p className="text-2xl font-bold text-green-700">
              {score}
            </p>
          </div>
          <div className="bg-red-50 rounded-lg p-4">
            <p className="text-xs text-red-600 font-semibold uppercase mb-1">
              Incorrect
            </p>
            <p className="text-2xl font-bold text-red-700">
              {totalQuestions - score}
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="space-y-3">
          <button
            onClick={onRestart}
            className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold text-base hover:bg-blue-700 transition shadow-lg"
          >
            🔄 Play Again
          </button>
          
          <button
            onClick={() => window.location.href = '/leaderboard'}
            className="w-full bg-purple-600 text-white px-6 py-3 rounded-lg font-semibold text-base hover:bg-purple-700 transition shadow-lg"
          >
            🏆 View Leaderboard
          </button>
          
          <button
            onClick={() => window.location.href = '/home'}
            className="w-full bg-gray-200 text-gray-700 px-6 py-3 rounded-lg font-semibold text-base hover:bg-gray-300 transition shadow-lg"
          >
            🏠 Back to Home
          </button>
        </div>
      </div>
    </div>
  );
};

export default QuizGameOver;