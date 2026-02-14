const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000';

export async function createPoll(question, options) {
  const response = await fetch(`${API_URL}/api/polls`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ question, options }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to create poll');
  }

  return response.json();
}

export async function getPoll(pollId, voterIdentifier) {
  const response = await fetch(`${API_URL}/api/polls/${pollId}`, {
    headers: {
      'X-Voter-Id': voterIdentifier,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to fetch poll');
  }

  return response.json();
}

export async function votePoll(pollId, optionId, voterIdentifier) {
  const response = await fetch(`${API_URL}/api/polls/${pollId}/vote`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ optionId, voterIdentifier }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to vote');
  }

  return response.json();
}
