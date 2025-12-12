import Layout from '../components/Layout';
import useQuiz from '../hooks/useQuiz';
import QuizCard from '../components/quiz/QuizCard';
import QuizFeedback from '../components/quiz/QuizFeedback';
import QuizStats from '../components/quiz/QuizStats';
import QuizGameOver from '../components/quiz/QuizGameOver';

const QuizPage = () => {
  const {
    quizStatus,
    currentQuestion,
    score,
    skipsRemaining,
    countriesViewed,
    totalCountries,  // ✅ Already coming from useQuiz
    userAnswer,
    setUserAnswer,
    feedback,
    loading,
    error,
    startQuiz,
    checkAndSubmitAnswer,
    skipQuestion,
    finishQuiz,
    restartQuiz,
  } = useQuiz();

  // ❌ DELETE THIS LINE - totalCountries already comes from useQuiz
  // const [totalCountries, setTotalCountries] = useState(192);

  // Idle state - Start screen
  if (quizStatus === 'idle') {
    return (
      <Layout>
        <div className="min-h-screen bg-gray-100 py-6 px-4">
          <div className="max-w-xl mx-auto">
            <div className="bg-white rounded-xl shadow-lg p-6 text-center">
              <h1 className="text-3xl font-bold text-gray-800 mb-2">
                Flag Challenge
              </h1>
              <p className="text-base text-gray-600 mb-4">
                Test your knowledge of world flags!
              </p>

              {/* Info Box */}
              <div className="bg-blue-50 rounded-lg p-4 mb-6 text-left">
                <p className="text-sm text-gray-700 mb-2">
                  <strong>How to play:</strong>
                </p>
                <ul className="text-sm text-gray-700 space-y-1">
                  <li>• Type the country name for each flag</li>
                  <li>• Correct answer = Score +1, auto-advance</li>
                  <li>• Wrong answer = Try again (unlimited retries)</li>
                  <li>• Skip = Move to next flag (3 skips total)</li>
                  <li>• Game continues until you see all 192 flags!</li>
                </ul>
              </div>

              {/* Start Button */}
              <button
                onClick={startQuiz}
                disabled={loading}
                className="w-full bg-blue-600 text-white px-8 py-4 rounded-lg font-bold text-lg hover:bg-blue-700 transition shadow-lg disabled:opacity-50"
              >
                {loading ? 'Starting...' : 'Start Challenge'}
              </button>

              {/* Tips */}
              <div className="mt-4 text-xs text-gray-500">
                💡 Tip: Answers are case-insensitive and support common aliases
              </div>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  // Game Over state
  if (quizStatus === 'gameOver') {
    return (
      <Layout>
        <div className="min-h-screen bg-gray-100 py-6 px-4">
          <QuizGameOver
            score={score}
            countriesViewed={countriesViewed}
            totalCountries={totalCountries}  // ✅ Pass it here
            onRestart={restartQuiz}
          />
        </div>
      </Layout>
    );
  }

  // Playing state
  return (
    <Layout>
      <div className="min-h-screen bg-gray-100 py-6 px-4">
        <div className="max-w-5xl mx-auto">
          {/* Header */}
          <div className="text-center mb-4">
            <h1 className="text-3xl font-bold text-gray-800 mb-1">
              🎮 Flag Challenge - Endless Mode
            </h1>
            <p className="text-base text-gray-600">
              Get as many correct as you can!
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="max-w-2xl mx-auto mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          {/* Stats */}
          <QuizStats
            score={score}
            skipsRemaining={skipsRemaining}
            countriesViewed={countriesViewed}
            totalCountries={totalCountries}
          />

          {/* Quiz Card */}
          <QuizCard
            question={currentQuestion}
            userAnswer={userAnswer}
            onAnswerChange={setUserAnswer}
            onAutoCheck={checkAndSubmitAnswer}
            onSkip={skipQuestion}
            skipsRemaining={skipsRemaining}
            loading={loading}
            disabled={!!feedback}
          />

          {/* Feedback */}
          <QuizFeedback feedback={feedback} />

          {/* Give Up Button */}
          <div className="text-center mt-6">
            <button
              onClick={finishQuiz}
              className="bg-red-600 text-white px-8 py-3 rounded-lg font-semibold text-base hover:bg-red-700 transition shadow-lg"
            >
              🏳️ Give Up
            </button>
          </div>

          {/* Help Text */}
          {!feedback && (
            <div className="text-center mt-4">
              <p className="text-gray-600 text-xs">
                💡 Wrong answer? Try again! Correct answer moves you forward automatically.
              </p>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default QuizPage;