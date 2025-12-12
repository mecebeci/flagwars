const LearningCard = ({ card, isRevealed, onReveal }) => {
  if (!card) return null;

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="bg-white rounded-xl shadow-lg p-4">
        {/* Progress indicator */}
        <div className="mb-2 flex items-center justify-between">
          <span className="text-xs text-gray-500">
            Box {card.box_number}/5
          </span>
          <span className="text-xs text-gray-500">
            Accuracy: {card.accuracy_rate}%
          </span>
        </div>

        {/* Flag Image */}
        <div className="w-full h-48 flex items-center justify-center mb-3">
          <img
            src={card.flag_image_url}
            alt="Flag"
            className="max-w-full max-h-full object-contain rounded-lg shadow-lg"
            onError={(e) => {
              e.target.src = 'https://via.placeholder.com/600x400?text=Flag';
            }}
          />
        </div>

        {/* Answer Section */}
        {!isRevealed ? (
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-3">
              🤔 What country is this?
            </p>
            <button
              onClick={onReveal}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold text-sm hover:bg-blue-700 transition shadow-lg"
            >
              👁️ Reveal Answer
            </button>
          </div>
        ) : (
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-800 mb-1">
              {card.country_name}
            </h2>
            <p className="text-base text-gray-500 font-mono">
              {card.country_code} {card.flag_emoji}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default LearningCard;