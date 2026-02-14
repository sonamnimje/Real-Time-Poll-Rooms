# 📁 Project Structure

```
Real-Time Poll Rooms/
│
├── 📄 README.md                    # Complete documentation
├── 📄 SUBMISSION.md                # Submission summary
├── 📄 PROJECT_STRUCTURE.md         # This overview
├── 📄 package.json                 # Root package (helper scripts)
├── 📄 .gitignore                   # Git ignore rules
│
├── 🐳 Docker Files
│   ├── docker-compose.yml          # Run both services
│   ├── Dockerfile.server           # Backend container
│   ├── Dockerfile.client           # Frontend container
│   └── nginx.conf                  # Nginx config for frontend
│
├── ☁️ railway.json                 # Railway deployment config
│
├── 📁 backend/                     # BACKEND (FastAPI + Socket.IO)
│   │
│   ├── 📄 requirements.txt         # Python dependencies
│   ├── 📄 main.py                  # FastAPI + Socket.IO app
│   ├── 📄 db.py                    # SQLite database logic
│   ├── 📄 .env.example             # Environment variables template
│   ├── 📄 .gitignore               # Backend ignore rules
│   └── 🗄️ polls.db                 # SQLite database (created on first run)
│
└── 📁 frontend/                    # FRONTEND (React)
    │
   ├── 📄 package.json             # Frontend dependencies
    ├── 📄 vite.config.js           # Vite configuration
    ├── 📄 index.html               # HTML entry point
    ├── 📄 .env.example             # Environment variables template
    ├── 📄 .gitignore               # Client ignore rules
    │
    └── 📁 src/
        │
        ├── 📄 main.jsx             # React entry point
        ├── 📄 App.jsx              # Main app component (routing)
        ├── 📄 api.js               # API client functions
        ├── 📄 utils.js             # Browser fingerprinting
        ├── 📄 index.css            # Global styles
        │
        └── 📁 pages/
            ├── 📄 CreatePoll.jsx   # Create poll page
            └── 📄 ViewPoll.jsx     # View/vote poll page


KEY FILES TO UNDERSTAND:

Backend (backend/):
├── server.js         → Express server, Socket.IO setup, API endpoints
└── database.js       → SQLite tables, queries, vote validation

Frontend (frontend/src/):
├── pages/CreatePoll.jsx  → Form to create new polls
├── pages/ViewPoll.jsx    → Display poll, handle voting, real-time updates
├── api.js                → HTTP requests to backend
└── utils.js              → Browser fingerprinting for anti-abuse

Documentation:
├── README.md             → Full project documentation
└── SUBMISSION.md         → Challenge requirements summary
```

## 🎯 File Purposes

### Documentation Files
- **GETTING_STARTED.md** - Your first stop! Quick setup and testing
- **README.md** - Complete documentation with all details
- **QUICKSTART.md** - Fast installation guide
- **DEPLOYMENT.md** - Step-by-step deployment instructions
- **SUBMISSION.md** - Summary for challenge submission

### Backend Files (server/)
- **server.js** - Express API + Socket.IO real-time server
- **database.js** - SQLite database setup and queries
- **package.json** - Dependencies: express, socket.io, better-sqlite3

### Frontend Files (client/)
- **src/pages/CreatePoll.jsx** - Poll creation form
- **src/pages/ViewPoll.jsx** - Poll display and voting interface
- **src/api.js** - HTTP client for backend API
- **src/utils.js** - Browser fingerprinting for voter identification
- **src/App.jsx** - React Router setup
- **src/index.css** - All styling (beautiful gradient theme!)

### Configuration Files
- **vite.config.js** - Vite build configuration
- **.env.example** - Environment variable templates
- **docker-compose.yml** - Docker orchestration
- **Dockerfile.*** - Container definitions
- **railway.json** - Railway deployment settings

## 🔄 How Data Flows

```
1. CREATE POLL
   User Input → CreatePoll.jsx → api.js → POST /api/polls → database.js → SQLite
   
2. VIEW POLL
   URL → ViewPoll.jsx → api.js → GET /api/polls/:id → database.js → SQLite → Display
   
3. VOTE ON POLL
   Click Option → ViewPoll.jsx → api.js → POST /api/polls/:id/vote → database.js → SQLite
   
4. REAL-TIME UPDATE
   Vote Saved → server.js emits 'poll-update' via Socket.IO → All connected clients receive update → ViewPoll.jsx updates UI
```

## 🛠️ Technology Stack Overview

```
Frontend:
├── React 18          (UI framework)
├── Vite              (Build tool)
├── React Router      (Routing)
└── Socket.IO Client  (WebSocket)

Backend:
├── Node.js           (Runtime)
├── Express           (Web framework)
├── Socket.IO         (WebSocket server)
├── better-sqlite3    (Database)
└── nanoid            (ID generation)

Database:
└── SQLite            (Lightweight, file-based)
    ├── polls table
    ├── options table
    └── votes table
```

## 📊 Database Schema

```sql
polls
├── id (TEXT, PRIMARY KEY)
├── question (TEXT)
└── created_at (INTEGER)

options
├── id (INTEGER, PRIMARY KEY, AUTOINCREMENT)
├── poll_id (TEXT, FOREIGN KEY → polls.id)
└── text (TEXT)

votes
├── id (INTEGER, PRIMARY KEY, AUTOINCREMENT)
├── poll_id (TEXT, FOREIGN KEY → polls.id)
├── option_id (INTEGER, FOREIGN KEY → options.id)
├── voter_identifier (TEXT)
├── ip_address (TEXT)
├── voted_at (INTEGER)
└── UNIQUE(poll_id, voter_identifier)
    UNIQUE(poll_id, ip_address)
```

## 🚀 Quick Commands

```powershell
# Install everything
cd backend && npm install && cd ..\frontend && npm install

# Run backend
cd backend && npm run dev

# Run frontend (different terminal)
cd frontend && npm run dev

# Build for production
cd frontend && npm run build

# Run with Docker
docker-compose up -d
```

---

**Ready to begin?** Open [GETTING_STARTED.md](GETTING_STARTED.md) for setup instructions! 🎉
