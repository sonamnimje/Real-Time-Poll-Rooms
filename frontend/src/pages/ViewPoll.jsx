import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { io } from 'socket.io-client';
import { getPoll, votePoll } from '../api';
import { getVoterIdentifier } from '../utils';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000';

function ViewPoll() {
  const { pollId } = useParams();
  const navigate = useNavigate();
  const [poll, setPoll] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedOption, setSelectedOption] = useState(null);
  const [hasVoted, setHasVoted] = useState(false);
  const [voting, setVoting] = useState(false);
  const [connected, setConnected] = useState(false);
  const socketRef = useRef(null);
  const voterIdentifier = useRef(getVoterIdentifier());

  useEffect(() => {
    // Fetch initial poll data
    async function fetchPoll() {
      try {
        const data = await getPoll(pollId, voterIdentifier.current);
        setPoll(data);
        setHasVoted(data.hasVoted);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    }

    fetchPoll();

    // Setup Socket.IO connection
    socketRef.current = io(API_BASE_URL);

    socketRef.current.on('connect', () => {
      console.log('Socket connected');
      setConnected(true);
      socketRef.current.emit('join-poll', pollId);
    });

    socketRef.current.on('disconnect', () => {
      console.log('Socket disconnected');
      setConnected(false);
    });

    socketRef.current.on('poll-update', (updatedPoll) => {
      console.log('Received poll update:', updatedPoll);
      setPoll(updatedPoll);
    });

    // Cleanup
    return () => {
      if (socketRef.current) {
        socketRef.current.emit('leave-poll', pollId);
        socketRef.current.disconnect();
      }
    };
  }, [pollId]);

  const handleVote = async () => {
    if (!selectedOption || hasVoted || voting) return;

    setVoting(true);
    setError('');

    try {
      const result = await votePoll(pollId, selectedOption, voterIdentifier.current);
      setPoll(result.pollData);
      setHasVoted(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setVoting(false);
    }
  };

  const copyShareLink = () => {
    const link = window.location.href;
    navigator.clipboard.writeText(link).then(() => {
      alert('Link copied to clipboard!');
    });
  };

  if (loading) {
    return (
      <div className="container">
        <div className="loading">Loading poll...</div>
      </div>
    );
  }

  if (error && !poll) {
    return (
      <div className="container">
        <div className="error-page">
          <h2>😕 Oops!</h2>
          <p>{error}</p>
          <button onClick={() => navigate('/')} className="btn btn-primary">
            Create a New Poll
          </button>
        </div>
      </div>
    );
  }

  const totalVotes = poll.totalVotes;

  return (
    <div className="container">
      <div className="header">
        <h1>
          📊 Poll
          <span className={`status-badge ${connected ? '' : 'disconnected'}`}>
            {connected ? 'Live' : 'Offline'}
          </span>
        </h1>
      </div>

      {error && (
        <div className="alert alert-error">
          {error}
        </div>
      )}

      {hasVoted && (
        <div className="alert alert-success">
          ✓ Your vote has been recorded!
        </div>
      )}

      <div className="poll-question">{poll.question}</div>

      <div className="poll-options">
        {poll.options.map((option) => {
          const percentage = totalVotes > 0 
            ? Math.round((option.votes / totalVotes) * 100) 
            : 0;
          
          const isSelected = selectedOption === option.id;

          return (
            <div
              key={option.id}
              className={`poll-option ${hasVoted ? 'voted' : ''} ${isSelected ? 'selected' : ''}`}
              onClick={() => !hasVoted && setSelectedOption(option.id)}
            >
              <div 
                className="option-progress" 
                style={{ width: `${percentage}%` }}
              />
              <div className="option-content">
                <span className="option-text">{option.text}</span>
                {hasVoted && (
                  <div className="option-stats">
                    <span className="option-percentage">{percentage}%</span>
                    <span className="option-votes">
                      {option.votes} {option.votes === 1 ? 'vote' : 'votes'}
                    </span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {!hasVoted && (
        <button
          className="btn btn-primary btn-block"
          onClick={handleVote}
          disabled={!selectedOption || voting}
          style={{ marginTop: '1.5rem' }}
        >
          {voting ? 'Submitting...' : 'Submit Vote'}
        </button>
      )}

      <div className="total-votes">
        Total Votes: {totalVotes}
      </div>

      <div className="share-section">
        <h3>Share this poll</h3>
        <p>Copy the link below to share with others:</p>
        <div className="share-link">
          <input
            type="text"
            value={window.location.href}
            readOnly
          />
          <button className="btn btn-primary" onClick={copyShareLink}>
            Copy
          </button>
        </div>
      </div>

      <button
        onClick={() => navigate('/')}
        className="back-button"
        style={{ width: '100%', marginTop: '1rem' }}
      >
        Create Another Poll
      </button>
    </div>
  );
}

export default ViewPoll;
