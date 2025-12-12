const LearningStats = ({ stats, currentIndex, totalCards }) => {
  if (!stats) return null;

  return (
    <div className="bg-white rounded-lg shadow-md p-4 mb-4">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Session Progress */}
        <div className="text-center">
          <p className="text-xs text-gray-600 font-semibold uppercase mb-1">
            Session
          </p>
          <p className="text-2xl font-bold text-blue-600">
            {currentIndex + 1}/{totalCards}
          </p>
        </div>

        {/* Due Cards */}
        <div className="text-center">
          <p className="text-xs text-gray-600 font-semibold uppercase mb-1">
            Due Today
          </p>
          <p className="text-2xl font-bold text-orange-600">
            {stats.due_flags}
          </p>
        </div>

        {/* Total Learning */}
        <div className="text-center">
          <p className="text-xs text-gray-600 font-semibold uppercase mb-1">
            Learning
          </p>
          <p className="text-2xl font-bold text-purple-600">
            {stats.total_flags}
          </p>
        </div>

        {/* Accuracy */}
        <div className="text-center">
          <p className="text-xs text-gray-600 font-semibold uppercase mb-1">
            Accuracy
          </p>
          <p className="text-2xl font-bold text-green-600">
            {stats.average_accuracy}%
          </p>
        </div>
      </div>

      {/* Box Distribution */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-600 font-semibold uppercase mb-2 text-center">
          Box Distribution
        </p>
        <div className="flex justify-center gap-3">
          {[1, 2, 3, 4, 5].map((box) => (
            <div key={box} className="text-center">
              <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center mb-1">
                <span className="font-bold text-blue-700 text-sm">{box}</span>
              </div>
              <span className="text-xs text-gray-600">
                {stats.box_distribution[`box_${box}`] || 0}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default LearningStats;