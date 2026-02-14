// Generate a unique identifier for this voter (browser fingerprint)
export function getVoterIdentifier() {
  let voterId = localStorage.getItem('voter_id');
  
  if (!voterId) {
    // Create a unique ID based on browser characteristics + random component
    const browserFingerprint = [
      navigator.userAgent,
      navigator.language,
      screen.width,
      screen.height,
      screen.colorDepth,
      new Date().getTimezoneOffset(),
      !!window.sessionStorage,
      !!window.localStorage,
    ].join('|');
    
    // Hash-like function to create a shorter identifier
    let hash = 0;
    for (let i = 0; i < browserFingerprint.length; i++) {
      const char = browserFingerprint.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    
    // Add random component and timestamp to make it more unique
    voterId = `voter_${Math.abs(hash)}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('voter_id', voterId);
  }
  
  return voterId;
}
