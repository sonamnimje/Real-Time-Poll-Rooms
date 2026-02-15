// Prefer env override, fall back to same origin to keep backend/frontend in sync
const API_URL = import.meta.env.VITE_API_URL || window.location.origin;

async function parseJsonSafe(response) {
  try {
    return await response.json();
  } catch (err) {
    return null; // Empty or non-JSON body
  }
}

async function parseTextSafe(response) {
  try {
    return await response.text();
  } catch (err) {
    return null;
  }
}

async function handleResponse(response, fallbackMessage) {
  const data = await parseJsonSafe(response);
  const textFallback = data ? null : await parseTextSafe(response);
  if (!response.ok) {
    const message =
      (data && (data.error || data.detail)) ||
      (textFallback && textFallback.trim()) ||
      `${fallbackMessage} (HTTP ${response.status})`;
    throw new Error(message);
  }
  return data;
}

export async function createPoll(question, options) {
  try {
    const response = await fetch(`${API_URL}/api/polls`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question, options }),
    });

    return await handleResponse(response, 'Failed to create poll');
  } catch (err) {
    // Network or parsing error
    throw new Error(err.message || 'Network error while creating poll');
  }
}

export async function getPoll(pollId, voterIdentifier) {
  try {
    const response = await fetch(`${API_URL}/api/polls/${pollId}`, {
      headers: {
        'X-Voter-Id': voterIdentifier,
      },
    });

    return await handleResponse(response, 'Failed to fetch poll');
  } catch (err) {
    throw new Error(err.message || 'Network error while fetching poll');
  }
}

export async function votePoll(pollId, optionId, voterIdentifier) {
  try {
    const response = await fetch(`${API_URL}/api/polls/${pollId}/vote`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ optionId, voterIdentifier }),
    });

    return await handleResponse(response, 'Failed to vote');
  } catch (err) {
    throw new Error(err.message || 'Network error while voting');
  }
}
