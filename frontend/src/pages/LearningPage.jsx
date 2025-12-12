import { useEffect } from 'react';
import Layout from '../components/Layout';
import useLearn from '../hooks/useLearn';
import LearningCard from '../components/learn/LearningCard';
import ReviewButtons from '../components/learn/ReviewButtons';
import LearningStats from '../components/learn/LearningStats';

const LearningPage = () => {
  const {
    learningStatus,
    currentCard,
    isRevealed,
    dueCards,
    currentIndex,
    stats,
    error,
    startLearning,
    addNewCards,
    revealAnswer,
    submitReview,
    restart,
    fetchStats,
  } = useLearn();

  // Fetch stats on mount
  useEffect(() => {
    fetchStats();
  }, []);

  // Idle state - Start screen
  if (learningStatus === 'idle') {
    return (
      <Layout>
        <div className="min-h-screen bg-gradient-to-br from-purple-400 via-pink-500 to-red-500 py-6 px-4">
          <div className="max-w-xl mx-auto">
            <div className="bg-white rounded-xl shadow-lg p-6 text-center">
              <h1 className="text-3xl font-bold text-gray-800 mb-2">
                🧠 Spaced Repetition Learning
              </h1>
              <p className="text-base text-gray-600 mb-4">
                Master flags using the proven Leitner System
              </p>

              {/* Stats Preview */}
              {stats && (
                <div className="bg-blue-50 rounded-lg p-4 mb-4">
                  <div className="grid grid-cols-3 gap-3 text-center">
                    <div>
                      <p className="text-2xl font-bold text-blue-600">
                        {stats.due_flags}
                      </p>
                      <p className="text-xs text-gray-600">Due Today</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-purple-600">
                        {stats.total_flags}
                      </p>
                      <p className="text-xs text-gray-600">Learning</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-green-600">
                        {stats.average_accuracy}%
                      </p>
                      <p className="text-xs text-gray-600">Accuracy</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="space-y-3">
                <button
                  onClick={startLearning}
                  className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold text-base hover:bg-blue-700 transition shadow-lg"
                >
                  📚 Start Learning Session
                </button>
                
                <button
                  onClick={() => addNewCards(10)}
                  className="w-full bg-green-600 text-white px-6 py-3 rounded-lg font-semibold text-base hover:bg-green-700 transition shadow-lg"
                >
                  ➕ Add 10 New Flags
                </button>
              </div>

              {/* Info Box */}
              <div className="mt-4 bg-gray-50 rounded-lg p-3 text-left">
                <p className="text-xs text-gray-700">
                  <strong>How it works:</strong>
                  <br />
                  • Flags you know well appear less often
                  <br />
                  • Flags you struggle with appear more often
                  <br />
                  • 5 boxes: daily → weekly → monthly reviews
                </p>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  // Loading state
  if (learningStatus === 'loading') {
    return (
      <Layout>
        <div className="min-h-screen bg-gradient-to-br from-blue-400 via-indigo-500 to-purple-600 flex items-center justify-center">
          <div className="bg-white rounded-xl shadow-lg p-8 text-center">
            <div className="text-5xl mb-3">🧠</div>
            <p className="text-xl font-bold text-gray-800">Loading cards...</p>
          </div>
        </div>
      </Layout>
    );
  }

  // No cards available
  if (learningStatus === 'noCards') {
    return (
      <Layout>
        <div className="min-h-screen bg-gradient-to-br from-yellow-400 via-orange-500 to-red-500 py-6 px-4">
          <div className="max-w-xl mx-auto">
            <div className="bg-white rounded-xl shadow-lg p-6 text-center">
              <div className="text-6xl mb-4">🎉</div>
              <h1 className="text-3xl font-bold text-gray-800 mb-2">
                All Caught Up!
              </h1>
              <p className="text-base text-gray-600 mb-4">
                No cards are due for review right now.
              </p>

              <div className="space-y-3">
                <button
                  onClick={() => addNewCards(10)}
                  className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold text-base hover:bg-blue-700 transition shadow-lg"
                >
                  ➕ Add More Flags to Learn
                </button>
                
                <button
                  onClick={() => window.location.href = '/home'}
                  className="w-full bg-gray-200 text-gray-700 px-6 py-3 rounded-lg font-semibold text-base hover:bg-gray-300 transition shadow-lg"
                >
                  🏠 Back to Home
                </button>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  // Session complete
  if (learningStatus === 'complete') {
    return (
      <Layout>
        <div className="min-h-screen bg-gradient-to-br from-green-400 via-teal-500 to-blue-600 py-6 px-4">
          <div className="max-w-xl mx-auto">
            <div className="bg-white rounded-xl shadow-lg p-6 text-center">
              <div className="text-6xl mb-4">✅</div>
              <h1 className="text-3xl font-bold text-gray-800 mb-2">
                Session Complete!
              </h1>
              <p className="text-base text-gray-600 mb-4">
                You reviewed {dueCards.length} flags
              </p>

              {stats && (
                <div className="bg-green-50 rounded-lg p-4 mb-4">
                  <p className="text-base text-gray-700">
                    Overall Accuracy: <strong>{stats.average_accuracy}%</strong>
                  </p>
                </div>
              )}

              <div className="space-y-3">
                <button
                  onClick={restart}
                  className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold text-base hover:bg-blue-700 transition shadow-lg"
                >
                  🔄 Start Another Session
                </button>
                
                <button
                  onClick={() => window.location.href = '/home'}
                  className="w-full bg-gray-200 text-gray-700 px-6 py-3 rounded-lg font-semibold text-base hover:bg-gray-300 transition shadow-lg"
                >
                  🏠 Back to Home
                </button>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  // Reviewing state
  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-blue-400 via-indigo-500 to-purple-600 py-6 px-4">
        <div className="max-w-5xl mx-auto">
          {/* Header */}
          <div className="text-center mb-4">
            <h1 className="text-3xl font-bold text-white mb-1">
              🧠 Learning Session
            </h1>
            <p className="text-base text-white/90">
              Review and master your flags
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="max-w-2xl mx-auto mb-6 bg-red-100 border border-red-400 text-red-700 px-6 py-4 rounded-lg">
              {error}
            </div>
          )}

          {/* Stats */}
          <LearningStats 
            stats={stats} 
            currentIndex={currentIndex} 
            totalCards={dueCards.length} 
          />

          {/* Learning Card */}
          <LearningCard
            card={currentCard}
            isRevealed={isRevealed}
            onReveal={revealAnswer}
          />

          {/* Review Buttons (only show when revealed) */}
          {isRevealed && (
            <ReviewButtons
              onCorrect={() => submitReview(true)}
              onIncorrect={() => submitReview(false)}
            />
          )}

          {/* Help Text */}
          <div className="text-center mt-4">
            <p className="text-white/80 text-xs">
              {!isRevealed 
                ? "💡 Try to recall the country name before revealing"
                : "💡 Be honest with yourself - this helps you learn better"
              }
            </p>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default LearningPage;