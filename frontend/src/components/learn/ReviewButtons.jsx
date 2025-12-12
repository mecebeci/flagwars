const ReviewButtons = ({ onCorrect, onIncorrect, disabled }) => {
  return (
    <div className="flex justify-center gap-4 mt-4">
      <button
        onClick={onIncorrect}
        disabled={disabled}
        className="bg-red-500 text-white px-6 py-4 rounded-lg font-semibold text-base hover:bg-red-600 transition shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex flex-col items-center gap-1"
      >
        <span className="text-2xl">❌</span>
        <span>I Didn't Know</span>
        <span className="text-xs font-normal opacity-75">Reset to Box 1</span>
      </button>

      <button
        onClick={onCorrect}
        disabled={disabled}
        className="bg-green-500 text-white px-6 py-4 rounded-lg font-semibold text-base hover:bg-green-600 transition shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex flex-col items-center gap-1"
      >
        <span className="text-2xl">✅</span>
        <span>I Knew It!</span>
        <span className="text-xs font-normal opacity-75">Move to next box</span>
      </button>
    </div>
  );
};

export default ReviewButtons;