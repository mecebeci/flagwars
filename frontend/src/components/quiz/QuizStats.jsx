const QuizStats = ({ questionNumber, totalQuestions, score }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-4 mb-4">
      <div className="grid grid-cols-3 gap-4 text-center">
        {/* Question Progress */}
        <div>
          <p className="text-xs text-gray-600 font-semibold uppercase mb-1">
            Question
          </p>
          <p className="text-2xl font-bold text-blue-600">
            {questionNumber}/{totalQuestions}
          </p>
        </div>

        {/* Current Score */}
        <div>
          <p className="text-xs text-gray-600 font-semibold uppercase mb-1">
            Score
          </p>
          <p className="text-2xl font-bold text-green-600">
            {score}
          </p>
        </div>

        {/* Accuracy */}
        <div>
          <p className="text-xs text-gray-600 font-semibold uppercase mb-1">
            Accuracy
          </p>
          <p className="text-2xl font-bold text-purple-600">
            {questionNumber > 0 ? Math.round((score / questionNumber) * 100) : 0}%
          </p>
        </div>
      </div>
    </div>
  );
};

export default QuizStats;