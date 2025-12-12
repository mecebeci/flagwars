import { useEffect, useRef } from 'react';

const QuizCard = ({ question, userAnswer, onAnswerChange, onAutoCheck, onSkip, skipsRemaining, loading, disabled }) => {
  const inputRef = useRef(null);

  // Auto-focus input when question changes
  useEffect(() => {
    if (inputRef.current && !disabled) {
      inputRef.current.focus();
    }
  }, [question, disabled]);

  // Keep focus on input at all times
  useEffect(() => {
    const interval = setInterval(() => {
      if (inputRef.current && document.activeElement !== inputRef.current && !disabled) {
        inputRef.current.focus();
      }
    }, 100);

    return () => clearInterval(interval);
  }, [disabled]);

  if (loading && !question) {
    return (
      <div className="w-full max-w-2xl mx-auto">
        <div className="bg-white rounded-xl shadow-lg p-8 text-center">
          <div className="text-4xl mb-3">🎮</div>
          <p className="text-lg font-semibold text-gray-800">Loading question...</p>
        </div>
      </div>
    );
  }

  if (!question) return null;

  const handleInputChange = (e) => {
    const value = e.target.value;
    onAnswerChange(value);
    
    // Auto-check answer as user types
    if (value.trim().length >= 3) {
      onAutoCheck(value);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="bg-white rounded-xl shadow-lg p-4">
        {/* Flag Image */}
        <div className="w-full h-48 flex items-center justify-center mb-4">
          <img
            src={question.flag_image_url}
            alt="Flag to identify"
            className="max-w-full max-h-full object-contain rounded-lg shadow-lg"
            onError={(e) => {
              e.target.src = 'https://via.placeholder.com/600x400?text=Flag';
            }}
          />
        </div>

        {/* Question */}
        <div className="text-center mb-4">
          <h2 className="text-xl font-bold text-gray-800 mb-2">
            🌍 Which country is this?
          </h2>
          <p className="text-sm text-gray-500">
            Country Code: {question.code}
          </p>
        </div>

        {/* Answer Input - No Submit Button! */}
        <div className="mb-4">
          <input
            ref={inputRef}
            type="text"
            value={userAnswer}
            onChange={handleInputChange}
            placeholder="Start typing the country name..."
            disabled={disabled || loading}
            className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 text-base disabled:bg-gray-100 disabled:cursor-not-allowed text-center font-semibold text-lg"
            autoComplete="off"
            autoFocus
          />
        </div>

        {/* Skip Button Only */}
        <div className="flex justify-center">
          <button
            type="button"
            onClick={onSkip}
            disabled={loading || skipsRemaining <= 0}
            className="bg-orange-600 text-white px-8 py-3 rounded-lg font-semibold text-base hover:bg-orange-700 transition shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            ⏭️ Skip ({skipsRemaining})
          </button>
        </div>
      </div>
    </div>
  );
};

export default QuizCard;