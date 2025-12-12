import { useEffect } from 'react';
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
    questionNumber,
    totalQuestions,
    score,
    userAnswer,
    setUserAnswer,
    feedback,
    loading,
    error,
    startQuiz,
    submitAnswer,
    nextQuestion,
    restartQuiz,
  } = useQuiz();

  // Idle state - Start screen
  if (quizStatus === 'idle') {
    return (
      <Layout>
        <div className="min-h-screen bg-gradient-to-br from-indigo-400 via-purple-500 to-pink-500 py-6 px-4">
          <div className="max-w-xl mx-auto">
            <div className="bg-white rounded-xl shadow-lg p-6 text-center">
              <h1 className="text-3xl font-bold text-gray-800 mb-2">
                🎮 Flag Quiz Game
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
                  <li>• 10 random flags will be shown</li>
                  <li>• Type the country name for each flag</li>
                  <li>• Get instant feedback on your answers</li>
                  <li>• Compete on the global leaderboard!</li>
                </ul>
              </div>

              {/* Start Button */}
              <button
                onClick={startQuiz}
                disabled={loading}
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-lg font-bold text-lg hover:from-blue-700 hover:to-purple-700 transition shadow-lg disabled:opacity-50"
              >
                {loading ? 'Starting...' : '🚀 Start Quiz'}
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
        <div className="min-h-screen bg-gradient-to-br from-green-400 via-teal-500 to-blue-600 py-6 px-4">
          <QuizGameOver
            score={score}
            totalQuestions={totalQuestions}
            onRestart={restartQuiz}
          />
        </div>
      </Layout>
    );
  }

  // Playing state
  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-blue-400 via-indigo-500 to-purple-600 py-6 px-4">
        <div className="max-w-5xl mx-auto">
          {/* Header */}
          <div className="text-center mb-4">
            <h1 className="text-3xl font-bold text-white mb-1">
              🎮 Flag Quiz
            </h1>
            <p className="text-base text-white/90">
              Identify the country flag
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
            questionNumber={questionNumber}
            totalQuestions={totalQuestions}
            score={score}
          />

          {/* Quiz Card */}
          <QuizCard
            question={currentQuestion}
            userAnswer={userAnswer}
            onAnswerChange={setUserAnswer}
            onSubmit={submitAnswer}
            loading={loading}
            disabled={!!feedback}
          />

          {/* Feedback */}
          <QuizFeedback
            feedback={feedback}
            onNext={nextQuestion}
            isLastQuestion={questionNumber >= totalQuestions}
          />

          {/* Help Text */}
          {!feedback && (
            <div className="text-center mt-4">
              <p className="text-white/80 text-xs">
                💡 Type the country name and press Enter or click Submit
              </p>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default QuizPage;