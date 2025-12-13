import { useState, useRef, useCallback } from 'react';
import api from '../services/api';

const useQuiz = () => {
  const [quizStatus, setQuizStatus] = useState('idle'); // 'idle' | 'playing' | 'gameOver'
  const [sessionId, setSessionId] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [score, setScore] = useState(0);
  const [skipsRemaining, setSkipsRemaining] = useState(3);
  const [countriesViewed, setCountriesViewed] = useState(0);
  const [userAnswer, setUserAnswer] = useState('');
  const [feedback, setFeedback] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [totalCountries, setTotalCountries] = useState(192);

  // Refs for optimization
  const checkTimeoutRef = useRef(null);
  const lastCheckedAnswerRef = useRef('');

  // Start quiz
  const startQuiz = async () => {
    try {
      setLoading(true);
      setError(null);

      // Start game session
      const startResponse = await api.post('/game/start/', {});
      console.log('Game started:', startResponse.data);

      setSessionId(startResponse.data.id);
      setScore(0);
      setSkipsRemaining(3);
      setCountriesViewed(0);
      setFeedback(null);
      setUserAnswer('');
      lastCheckedAnswerRef.current = '';

      // Fetch first question
      await fetchQuestion();

      setQuizStatus('playing');

    } catch (err) {
      console.error('Failed to start quiz:', err);
      setError('Failed to start quiz. Please try again.');
      setQuizStatus('idle');
    } finally {
      setLoading(false);
    }
  };


  // Fetch current/next question
  const fetchQuestion = async () => {
    try {
      setLoading(true);
      setError(null);
      setFeedback(null);
      setUserAnswer('');
      lastCheckedAnswerRef.current = '';

      const response = await api.get('/game/question/');
      console.log('Got question:', response.data);

      // Check if game is auto-completed (all countries viewed)
      if (response.data.game_completed) {
        console.log('🎉 All countries completed!');
        setScore(response.data.final_score);
        setCountriesViewed(response.data.countries_viewed);
        setTotalCountries(response.data.total_countries || 192);
        setQuizStatus('gameOver');
        return;
      }

      setCurrentQuestion({
        id: response.data.id,
        flag_image_url: response.data.flag_image_url,
        code: response.data.code,
      });

      setScore(response.data.score);
      setSkipsRemaining(response.data.skips_remaining);
      setCountriesViewed(response.data.countries_viewed);

    } catch (err) {
      console.error('Failed to fetch question:', err);
      
      // Check if error is game completion
      if (err.response?.data?.game_completed) {
        setQuizStatus('gameOver');
      } else {
        setError('Failed to load question. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  // Auto-check answer with debouncing and duplicate prevention
  const checkAndSubmitAnswer = useCallback(async (answer) => {
    const trimmedAnswer = answer.trim();
    
    // Don't check if:
    // 1. Too short (less than 3 chars)
    // 2. Same as last checked answer (avoid duplicate API calls)
    if (trimmedAnswer.length < 3 || trimmedAnswer.toLowerCase() === lastCheckedAnswerRef.current.toLowerCase()) {
      return;
    }

    // Clear previous timeout (debouncing)
    if (checkTimeoutRef.current) {
      clearTimeout(checkTimeoutRef.current);
    }

    // Debounce: wait 400ms after user stops typing
    checkTimeoutRef.current = setTimeout(async () => {
      try {
        console.log('Checking answer:', trimmedAnswer);
        
        // Remember what we're checking to avoid duplicates
        lastCheckedAnswerRef.current = trimmedAnswer;
        
        const response = await api.post('/game/answer/', {
          answer: trimmedAnswer
        });

        console.log('Answer response:', response.data);

        // Only process if correct
        if (response.data.correct) {
          console.log('✅ Correct answer!');
          
          // Clear the last checked answer
          lastCheckedAnswerRef.current = '';
          
          // Show feedback
          setFeedback({
            correct: true,
            correctAnswer: response.data.correct_answer,
            autoAdvance: true
          });

          setScore(response.data.score);
          setUserAnswer(''); // Clear input immediately

          // Auto-fetch next question after short delay
          setTimeout(() => {
            setFeedback(null);
            fetchQuestion();
          }, 1000); // 1 second delay for user to see feedback
        }
        // If incorrect, do nothing (let user keep typing)

      } catch (err) {
        console.log('Auto-check error:', err);
        // Silently fail - don't show errors for auto-check
      }
    }, 400); // 400ms debounce delay
  }, []);

  // Manual submit (if needed for Enter key or button)
  const submitAnswer = async () => {
    if (!userAnswer.trim()) {
      setError('Please enter an answer');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const response = await api.post('/game/answer/', {
        answer: userAnswer.trim()
      });

      console.log('Answer response:', response.data);

      // Show feedback
      setFeedback({
        correct: response.data.correct,
        correctAnswer: response.data.correct_answer,
        autoAdvance: response.data.auto_advance
      });

      setScore(response.data.score);

      // If correct, auto-fetch next question
      if (response.data.auto_advance) {
        setUserAnswer('');
        setTimeout(() => {
          setFeedback(null);
          fetchQuestion();
        }, 1000);
      }

    } catch (err) {
      console.error('Failed to submit answer:', err);
      setError('Failed to submit answer. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Skip question
  const skipQuestion = async () => {
    if (skipsRemaining <= 0) {
      setError('No skips remaining!');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Clear any pending auto-checks
      if (checkTimeoutRef.current) {
        clearTimeout(checkTimeoutRef.current);
      }
      lastCheckedAnswerRef.current = '';

      const response = await api.post('/game/skip/');
      console.log('Skip response:', response.data);

      setSkipsRemaining(response.data.skips_remaining);
      setScore(response.data.score);
      setUserAnswer('');

      // Fetch next question
      await fetchQuestion();

    } catch (err) {
      console.error('Failed to skip question:', err);
      setError(err.response?.data?.error || 'Failed to skip question.');
    } finally {
      setLoading(false);
    }
  };

  // Give up / Finish quiz
  const finishQuiz = async (elapsedSeconds = 0) => {
    try {
      setLoading(true);

      // Clear any pending auto-checks
      if (checkTimeoutRef.current) {
        clearTimeout(checkTimeoutRef.current);
      }

      // ⏱️ Send elapsed time to backend
      const response = await api.post('/game/finish/', {
        time_elapsed_seconds: elapsedSeconds
      });
      
      console.log('Game finished:', response.data);

      // Update final stats
      if (response.data.stats) {
        setScore(response.data.stats.final_score);
        setCountriesViewed(response.data.stats.countries_viewed);
      }

      setQuizStatus('gameOver');
    } catch (err) {
      console.error('Failed to finish quiz:', err);
      // Still show game over even if backend fails
      setQuizStatus('gameOver');
    } finally {
      setLoading(false);
    }
  };

  // Restart quiz
  const restartQuiz = () => {
    // Clear any pending timeouts
    if (checkTimeoutRef.current) {
      clearTimeout(checkTimeoutRef.current);
    }
    
    setQuizStatus('idle');
    setSessionId(null);
    setCurrentQuestion(null);
    setScore(0);
    setSkipsRemaining(3);
    setCountriesViewed(0);
    setUserAnswer('');
    setFeedback(null);
    setError(null);
    lastCheckedAnswerRef.current = '';
  };

  return {
    quizStatus,
    sessionId,
    currentQuestion,
    score,
    skipsRemaining,
    countriesViewed,
    totalCountries,
    userAnswer,
    setUserAnswer,
    feedback,
    loading,
    error,
    startQuiz,
    submitAnswer,
    checkAndSubmitAnswer,
    skipQuestion,
    finishQuiz,
    restartQuiz,
  };
};

export default useQuiz;