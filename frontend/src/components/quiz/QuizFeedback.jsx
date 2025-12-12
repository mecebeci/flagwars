const QuizFeedback = ({ feedback }) => {
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

          {/* Show correct answer */}
          <p className="text-base text-gray-700 mb-2">
            The answer is: <strong>{feedback.correctAnswer}</strong>
          </p>

          {/* Auto-advance message */}
          {feedback.autoAdvance && (
            <p className="text-sm text-green-600">
              Moving to next flag...
            </p>
          )}
          
          {!feedback.autoAdvance && (
            <p className="text-sm text-gray-600">
              Try again or skip this question
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default QuizFeedback;