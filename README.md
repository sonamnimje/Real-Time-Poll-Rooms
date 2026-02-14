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

**Public URL**: [To be deployed]

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
   
   Backend (.env) - Already configured for local development:
   ```bash
   PORT=3000
   CORS_ORIGINS=http://localhost:5173,http://localhost:3000
   DB_PATH=./polls.db
   ```
   
   Frontend (.env) - Already configured for local development:
   ```bash
   VITE_API_URL=http://localhost:3000
   ```
   
   **Note:** The `.env` files are already created with default values for local development. You can modify them if needed, but they work out of the box.

5. **Start the backend server**
   ```bash
   cd backend
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uvicorn main:sio_app --reload --host 0.0.0.0 --port 3000
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
   - The "Live" badge indicates WebSocket connection is active
   - Open the same poll in multiple browser tabs/windows to see real-time updates!

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

```bash
# From project root
docker-compose up -d
```

This will start both the backend and frontend containers:
- Backend: http://localhost:3000
- Frontend: http://localhost:80

### Individual Containers

**Build and run backend:**
```bash
docker build -f Dockerfile.server -t poll-backend .
docker run -p 3000:3000 poll-backend
```

**Build and run frontend:**
```bash
docker build -f Dockerfile.client -t poll-frontend .
docker run -p 80:80 poll-frontend
```

## ☁️ Cloud Deployment

### Deploying to Railway

1. **Backend Deployment**
   - Create a new project on [Railway](https://railway.app)
   - Connect your GitHub repository
   - Set the root directory to `/backend`
   - Use Python builder; start command: `uvicorn main:sio_app --host 0.0.0.0 --port $PORT`
   - Add environment variable: `CORS_ORIGINS=https://your-frontend-url.vercel.app`
   - Note the generated URL (e.g., `https://your-app.railway.app`)

2. **Frontend Deployment**
   - Deploy to [Vercel](https://vercel.com) or [Netlify](https://netlify.com)
   - Set build command: `npm run build`
   - Set output directory: `dist`
   - Add environment variable: `VITE_API_URL=https://your-backend-url.railway.app`
   - Update CORS settings in backend to allow your frontend domain

3. **Environment Variables**
   
   Backend (Railway):
   ```
   PORT=3000
   CORS_ORIGINS=https://your-frontend-url.vercel.app
   ```
   
   Frontend (Vercel):
   ```
   VITE_API_URL=https://your-backend.railway.app
   ```

### Deploying to Render

1. Create a new Web Service
2. Connect your repository
3. Configure:
   - Build Command: `cd backend && pip install -r requirements.txt`
   - Start Command: `cd backend && uvicorn main:sio_app --host 0.0.0.0 --port $PORT`
4. Add environment variables as needed

## 📊 Database Schema

### Polls Table
```sql
CREATE TABLE polls (
  id TEXT PRIMARY KEY,
  question TEXT NOT NULL,
  created_at INTEGER NOT NULL
);
```

### Options Table
```sql
CREATE TABLE options (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  poll_id TEXT NOT NULL,
  text TEXT NOT NULL,
  FOREIGN KEY (poll_id) REFERENCES polls(id) ON DELETE CASCADE
);
```

### Votes Table
```sql
CREATE TABLE votes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  poll_id TEXT NOT NULL,
  option_id INTEGER NOT NULL,
  voter_identifier TEXT NOT NULL,
  ip_address TEXT NOT NULL,
  voted_at INTEGER NOT NULL,
  FOREIGN KEY (poll_id) REFERENCES polls(id) ON DELETE CASCADE,
  FOREIGN KEY (option_id) REFERENCES options(id) ON DELETE CASCADE,
  UNIQUE(poll_id, voter_identifier),
  UNIQUE(poll_id, ip_address)
);
```

## 🔄 How Real-Time Updates Work

1. **Client connects** to Socket.IO server when viewing a poll
2. **Joins poll room** identified by poll ID
3. **When any user votes**:
   - Vote is recorded in database
   - Server emits `poll-update` event to all clients in that poll's room
   - All connected clients receive updated vote counts instantly
4. **Connection status** displayed in UI (Live/Offline badge)
5. **No page refresh needed** - multiple users can vote simultaneously and see live updates

### Real-Time Architecture
- **Backend**: FastAPI + python-socketio for WebSocket server
- **Frontend**: React + socket.io-client for WebSocket client
- **Communication**: Bidirectional real-time events using Socket.IO protocol
- **Scalability**: Socket rooms ensure updates are only sent to users viewing the same poll

## 🎨 API Endpoints

### POST `/api/polls`
Create a new poll
```json
{
  "question": "What's your favorite color?",
  "options": ["Red", "Blue", "Green"]
}
```

### GET `/api/polls/:pollId`
Get poll data and check if user has voted

### POST `/api/polls/:pollId/vote`
Cast a vote
```json
{
  "optionId": 1,
  "voterIdentifier": "unique-voter-id"
}
```

## 🐛 Known Limitations

1. **Vote Manipulation**
   - Determined users with technical knowledge can bypass client-side restrictions
   - VPN/proxy users can change IPs
   - No CAPTCHA or rate limiting (to keep it simple)

2. **Scalability**
   - SQLite is file-based, not ideal for high-traffic production
   - For production, consider PostgreSQL or MongoDB
   - Socket.IO rooms stored in memory (use Redis adapter for multi-server)

3. **Poll Management**
   - No poll deletion or editing after creation
   - No admin panel
   - No poll expiration/archiving

4. **Security**
   - No user authentication
   - Anyone can create unlimited polls
   - No protection against poll creation spam

5. **Analytics**
   - No detailed voting analytics or demographics
   - No export functionality for results

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

## 📝 Testing

### Manual Testing Checklist

- [ ] Create a poll with valid data
- [ ] Create a poll with invalid data (empty question, < 2 options)
- [ ] Create a poll with duplicate options
- [ ] Vote on a poll
- [ ] Try to vote twice (should be prevented)
- [ ] Open poll in multiple browsers and watch real-time updates
- [ ] Test on mobile device
- [ ] Test with network disconnection
- [ ] Test shareable link copying
- [ ] Refresh page after voting (vote should persist)

## 📄 License

MIT

## 👤 Author

Developed for the Real-Time Poll Rooms coding challenge

## 🤝 Contributing

This is a challenge submission, but suggestions are welcome!

---

**Note**: Remember to replace placeholder URLs with actual deployment URLs before submission.
