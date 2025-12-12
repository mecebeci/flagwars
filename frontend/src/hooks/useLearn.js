import { useState, useEffect } from 'react';
import api from '../services/api';

const useLearn = () => {
  const [learningStatus, setLearningStatus] = useState('idle'); // 'idle' | 'loading' | 'reviewing' | 'noCards' | 'complete'
  const [currentCard, setCurrentCard] = useState(null);
  const [isRevealed, setIsRevealed] = useState(false);
  const [dueCards, setDueCards] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);
  
  // Fetch learning statistics
  const fetchStats = async () => {
    try {
      const response = await api.get('/learn/stats/');
      setStats(response.data);
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  };

  // Fetch due cards
  const fetchDueCards = async () => {
    try {
      setLearningStatus('loading');
      setError(null);
      
      const response = await api.get('/learn/due/?limit=10');
      
      if (response.data.count === 0) {
        setLearningStatus('noCards');
        setDueCards([]);
        setCurrentCard(null);
      } else {
        setDueCards(response.data.due_flags);
        setCurrentCard(response.data.due_flags[0]);
        setCurrentIndex(0);
        setIsRevealed(false);
        setLearningStatus('reviewing');
      }
      
      await fetchStats();
      
    } catch (err) {
      console.error('Failed to fetch due cards:', err);
      setError('Failed to load cards. Please try again.');
      setLearningStatus('idle');
    }
  };

  // Add new cards to learning
  const addNewCards = async (limit = 10) => {
    try {
      setLearningStatus('loading');
      setError(null);
      
      await api.post('/learn/add-new/', { limit });
      
      // Fetch the newly added cards
      await fetchDueCards();
      
    } catch (err) {
      console.error('Failed to add new cards:', err);
      setError('Failed to add new cards. Please try again.');
      setLearningStatus('idle');
    }
  };

  // Reveal the answer
  const revealAnswer = () => {
    setIsRevealed(true);
  };

  // Submit review
  const submitReview = async (isCorrect) => {
    if (!currentCard) return;
    
    try {
      await api.post('/learn/review/', {
        country_id: currentCard.country,
        is_correct: isCorrect
      });
      
      // Move to next card
      const nextIndex = currentIndex + 1;
      
      if (nextIndex >= dueCards.length) {
        // Completed all cards in this session
        setLearningStatus('complete');
        await fetchStats();
      } else {
        // Show next card
        setCurrentCard(dueCards[nextIndex]);
        setCurrentIndex(nextIndex);
        setIsRevealed(false);
      }
      
    } catch (err) {
      console.error('Failed to submit review:', err);
      setError('Failed to submit review. Please try again.');
    }
  };

  // Start learning session
  const startLearning = () => {
    fetchDueCards();
  };

  // Restart session
  const restart = () => {
    setLearningStatus('idle');
    setCurrentCard(null);
    setIsRevealed(false);
    setDueCards([]);
    setCurrentIndex(0);
    setError(null);
  };

  return {
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
  };
};

export default useLearn;