# 📊 Real-Time Poll Rooms

A modern, real-time polling web application that allows users to create polls, share them via links, and see live vote updates without page refreshes.

## 🎯 Features

- **Poll Creation**: Create polls with custom questions and multiple options (2-10)
- **Shareable Links**: Generate unique URLs for each poll
- **Real-Time Updates**: Live vote counting using WebSocket technology
- **Single Vote System**: One vote per user per poll
- **Persistence**: All polls and votes are stored in a database
- **Anti-Abuse**: Multiple mechanisms to prevent vote manipulation
- **Responsive Design**: Works on desktop and mobile devices

## 🚀 Live Demo

**Public URL**: https://real-time-pollrooms.vercel.app/

## 🛠️ Technology Stack

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Socket.IO Client** - Real-time communication

### Backend
- **FastAPI (Python)** - Web framework
- **Socket.IO (python-socketio)** - WebSocket server for real-time updates
- **SQLite (sqlite3)** - Database for persistence
- **Custom nanoid-style ID** - Unique ID generation

## 🔒 Anti-Abuse Mechanisms

### 1. IP Address Tracking
**What it prevents**: Multiple votes from the same network/device
**How it works**: 
- The server captures the client's IP address from request headers
- Each vote is associated with both the poll ID and IP address
- Database constraint prevents the same IP from voting twice on the same poll
- Works across different browsers and devices on the same network

**Limitations**:
- Users behind the same NAT/proxy share an IP address
- VPN users can change IPs to vote multiple times
- Dynamic IPs may allow re-voting after IP changes

### 2. Browser Fingerprinting
**What it prevents**: Multiple votes from the same browser session
**How it works**:
- Creates a unique identifier based on browser characteristics:
  - User agent string
  - Screen resolution and color depth
  - Language settings
  - Timezone offset
  - Storage capabilities
  - Random component for uniqueness
- Stored in localStorage, persists across page reloads
- Each vote requires this unique voter identifier
- Database constraint prevents the same identifier from voting twice

**Limitations**:
- Users can clear localStorage to get a new identifier
- Incognito/private browsing creates new sessions
- Different browsers on the same device can vote separately
- Advanced users can manipulate browser fingerprints

### Combined Effect
By using BOTH mechanisms together:
- A user must change BOTH their IP and browser fingerprint to vote again
- This significantly raises the barrier for casual abuse
- Most legitimate use cases (different people on different devices) work correctly

## ✅ Edge Cases Handled

1. **Empty/Invalid Input**
   - Validates question and option fields before poll creation
   - Minimum 2 options required, maximum 10 allowed
   - Trims whitespace and rejects empty strings

2. **Duplicate Options**
   - Checks for duplicate option text (case-insensitive)
   - Rejects poll creation if duplicates found

3. **Invalid Poll IDs**
   - Returns 404 error for non-existent polls
   - Validates poll ID format

4. **Race Conditions**
   - SQLite transactions ensure atomic poll creation
   - UNIQUE constraints prevent duplicate votes even in concurrent scenarios

5. **Network Disconnection**
   - Frontend displays connection status (Live/Offline)
   - Automatic reconnection when network restored
   - Cached poll data displayed during disconnection

6. **Already Voted**
   - Server checks both IP and voter ID before accepting vote
   - Returns appropriate error message
   - UI prevents re-voting and shows results instead

7. **Invalid Option Selection**
   - Validates option ID exists in the poll
   - Rejects votes for non-existent options

8. **Missing Headers**
   - Handles cases where voter ID or IP cannot be determined
   - Falls back to "anonymous" or "unknown" with graceful degradation

## 📦 Installation & Setup

### Prerequisites
- Python 3.11+
- Node.js 18+ 
- npm or yarn

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/sonamnimje/Real-Time-Poll-Rooms.git
   cd Real-Time-Poll-Rooms
   ```

2. **Install backend dependencies**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Install frontend dependencies**
   ```bash
   cd ../frontend
   npm install
   ```

4. **Set up environment variables**
   
   Backend (.env):
   ```bash
   cd ../backend
   cp .env.example .env
   # Edit .env if needed
   ```
   
   Frontend (.env):
   ```bash
   cd ../frontend
   cp .env.example .env
   # Edit VITE_API_URL if backend is on different host
   ```

5. **Start the backend server**
   ```bash
   cd ../backend
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uvicorn main:sio_app --reload --host 127.0.0.1 --port 3000
   # Backend runs on http://localhost:3000
   ```

6. **Start the frontend (in a new terminal)**
   ```bash
   cd frontend
   npm run dev
   # Frontend runs on http://localhost:5173
   ```

7. **Open the application**
   - Navigate to http://localhost:5173 in your browser


## 🔄 How Real-Time Updates Work

1. **Client connects** to Socket.IO server when viewing a poll
2. **Joins poll room** identified by poll ID
3. **When any user votes**:
   - Vote is recorded in database
   - Server emits `poll-update` event to all clients in that poll's room
   - All connected clients receive updated vote counts instantly
4. **Connection status** displayed in UI (Live/Offline badge)

## 🚀 Future Improvements

- [ ] Add CAPTCHA for vote verification
- [ ] Implement rate limiting on poll creation and voting
- [ ] Add poll expiration dates
- [ ] User accounts and authentication
- [ ] Poll editing and deletion
- [ ] Result export (CSV, PDF)
- [ ] Multiple choice polls (select multiple options)
- [ ] Real-time viewer count
- [ ] Poll templates
- [ ] Dark mode theme
- [ ] Email notifications
- [ ] Social media sharing integration


## 👤 Author

Developed for the Real-Time Poll Rooms coding challenge

## 🤝 Contributing

This is a challenge submission, but suggestions are welcome!

---