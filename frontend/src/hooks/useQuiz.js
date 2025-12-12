import { useState } from 'react';
import api from '../services/api';

const useQuiz = () => {
  const [quizStatus, setQuizStatus] = useState('idle');
  const [sessionId, setSessionId] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [questionNumber, setQuestionNumber] = useState(0);
  const [totalQuestions, setTotalQuestions] = useState(10);
  const [score, setScore] = useState(0);
  const [userAnswer, setUserAnswer] = useState('');
  const [feedback, setFeedback] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Start quiz
  const startQuiz = async () => {
    try {
      setLoading(true);
      setError(null);

      // 1. Start quiz session
      const startResponse = await api.post('/game/start/', {
        game_mode: 'quiz'
      });

      console.log('Started game session:', startResponse.data);
      setSessionId(startResponse.data.id);
      setScore(0);
      setQuestionNumber(0);
      setFeedback(null);
      setUserAnswer('');

      // 2. Fetch first question
      const questionResponse = await api.get('/game/question/');
      console.log('Got first question:', questionResponse.data);

      setCurrentQuestion({
        id: questionResponse.data.id,
        flag_image_url: questionResponse.data.flag_image_url,
        flag_emoji: questionResponse.data.flag_emoji,
        code: questionResponse.data.code,
      });

      setQuestionNumber(questionResponse.data.question_number);
      setTotalQuestions(questionResponse.data.total_questions);
      
      // 3. Set status to playing AFTER everything is loaded
      setQuizStatus('playing');

    } catch (err) {
      console.error('Failed to start quiz:', err);
      setError('Failed to start quiz. Please try again.');
      setQuizStatus('idle');
    } finally {
      setLoading(false);
    }
  };

  // Fetch next question
  const fetchQuestion = async () => {
    try {
      setLoading(true);
      setError(null);
      setFeedback(null);
      setUserAnswer('');

      const response = await api.get('/game/question/');
      console.log('Got next question:', response.data);

      setCurrentQuestion({
        id: response.data.id,
        flag_image_url: response.data.flag_image_url,
        flag_emoji: response.data.flag_emoji,
        code: response.data.code,
      });

      setQuestionNumber(response.data.question_number);
      setTotalQuestions(response.data.total_questions);

    } catch (err) {
      console.error('Failed to fetch question:', err);
      setError('Failed to load question. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Submit answer
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
        correctAnswer: response.data.correct_answer
      });

      setScore(response.data.score);

      // Check if game is complete
      if (response.data.is_completed) {
        // Finish game after a short delay
        setTimeout(async () => {
          await finishQuiz();
        }, 1500);
      }

    } catch (err) {
      console.error('Failed to submit answer:', err);
      setError('Failed to submit answer. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Move to next question
  const nextQuestion = () => {
    fetchQuestion();
  };

  // Finish quiz
  const finishQuiz = async () => {
    try {
      const response = await api.post('/game/finish/');
      console.log('Game finished:', response.data);
      setQuizStatus('gameOver');
    } catch (err) {
      console.error('Failed to finish quiz:', err);
      setQuizStatus('gameOver');
    }
  };

  // Restart quiz
  const restartQuiz = () => {
    setQuizStatus('idle');
    setSessionId(null);
    setCurrentQuestion(null);
    setQuestionNumber(0);
    setScore(0);
    setUserAnswer('');
    setFeedback(null);
    setError(null);
  };

  return {
    quizStatus,
    sessionId,
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
  };
};

export default useQuiz;