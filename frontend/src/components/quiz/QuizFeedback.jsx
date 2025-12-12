const QuizFeedback = ({ feedback, onNext, isLastQuestion }) => {
  if (!feedback) return null;

  return (
    <div className="w-full max-w-2xl mx-auto mt-4">
      <div className={`rounded-xl shadow-lg p-4 ${
        feedback.correct 
          ? 'bg-green-100 border-2 border-green-500' 
          : 'bg-red-100 border-2 border-red-500'
      }`}>
        <div className="text-center">
          {/* Icon and Message */}
          <div className="text-4xl mb-2">
            {feedback.correct ? '✅' : '❌'}
          </div>
          <h3 className={`text-xl font-bold mb-2 ${
            feedback.correct ? 'text-green-700' : 'text-red-700'
          }`}>
            {feedback.correct ? 'Correct!' : 'Incorrect'}
          </h3>

          {/* Show correct answer if wrong */}
          {!feedback.correct && (
            <p className="text-base text-gray-700 mb-3">
              The correct answer is: <strong>{feedback.correctAnswer}</strong>
            </p>
          )}

          {/* Next Button */}
          <button
            onClick={onNext}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold text-base hover:bg-blue-700 transition shadow-lg"
          >
            {isLastQuestion ? '🏁 See Results' : '➡️ Next Question'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default QuizFeedback;