const QuizCard = ({ question, userAnswer, onAnswerChange, onSubmit, loading, disabled }) => {
  if (loading && !question) {
    return <div className="text-center p-4">Yükleniyor...</div>;
  }

  if (!question) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit();
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

        {/* Answer Input */}
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <input
              type="text"
              value={userAnswer}
              onChange={(e) => onAnswerChange(e.target.value)}
              placeholder="Type the country name..."
              disabled={disabled || loading}
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 text-base disabled:bg-gray-100 disabled:cursor-not-allowed"
              autoFocus
            />
          </div>

          <button
            type="submit"
            disabled={disabled || loading || !userAnswer.trim()}
            className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold text-base hover:bg-blue-700 transition shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Checking...' : '✓ Submit Answer'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default QuizCard;