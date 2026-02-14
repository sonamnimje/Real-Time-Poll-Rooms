import os
import secrets
from typing import List

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
import socketio

from db import create_poll, get_poll_data, has_user_voted, cast_vote

PORT = int(os.getenv("PORT", "3000"))

# Allow origins from environment variable or default to development + production
allowed_origins_env = os.getenv("CORS_ORIGINS", "")
if allowed_origins_env:
    origins = [origin.strip() for origin in allowed_origins_env.split(",")]
else:
    origins = [
        "http://localhost:5173",
        "http://localhost:3000", 
        "https://real-time-pollrooms.vercel.app",
    ]

# Socket.IO server
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*"  # Allow all origins for WebSocket
)

app = FastAPI(title="Real-Time Poll Rooms API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sio_app = socketio.ASGIApp(sio, other_asgi_app=app)


def _make_poll_id(length: int = 10) -> str:
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip
    return request.client.host if request.client else "unknown"


class CreatePollRequest(BaseModel):
    question: str
    options: List[str]

    @field_validator("question")
    def validate_question(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Question is required")
        return v.strip()

    @field_validator("options")
    def validate_options(cls, v: List[str]) -> List[str]:
        valid = [opt.strip() for opt in v if opt and opt.strip()]
        if len(valid) < 2:
            raise ValueError("At least 2 valid options are required")
        lowered = [o.lower() for o in valid]
        if len(set(lowered)) != len(valid):
            raise ValueError("Duplicate options are not allowed")
        return valid


class VoteRequest(BaseModel):
    optionId: int
    voterIdentifier: str

    @field_validator("voterIdentifier")
    def validate_voter(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Voter identifier is required")
        return v.strip()


@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": __import__("time").time() * 1000}


@app.post("/api/polls")
async def create_poll_endpoint(payload: CreatePollRequest):
    poll_id = _make_poll_id()
    create_poll(poll_id, payload.question, payload.options)
    return {"pollId": poll_id, "shareLink": f"/poll/{poll_id}"}


@app.get("/api/polls/{poll_id}")
async def get_poll_endpoint(poll_id: str, request: Request):
    poll = get_poll_data(poll_id)
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")

    voter_identifier = request.headers.get("x-voter-id", "anonymous")
    ip_address = _client_ip(request)
    voted = has_user_voted(poll_id, voter_identifier, ip_address)

    return {**poll, "hasVoted": voted}


@app.post("/api/polls/{poll_id}/vote")
async def vote_endpoint(poll_id: str, payload: VoteRequest, request: Request):
    poll = get_poll_data(poll_id)
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")

    option_exists = any(opt["id"] == payload.optionId for opt in poll["options"])
    if not option_exists:
        raise HTTPException(status_code=400, detail="Invalid option")

    ip_address = _client_ip(request)
    if has_user_voted(poll_id, payload.voterIdentifier, ip_address):
        raise HTTPException(status_code=400, detail="You have already voted on this poll")

    success = cast_vote(poll_id, payload.optionId, payload.voterIdentifier, ip_address)
    if not success:
        raise HTTPException(status_code=400, detail="Vote failed - you may have already voted")

    updated_poll = get_poll_data(poll_id)
    await sio.emit("poll-update", updated_poll, room=f"poll-{poll_id}")

    return {"success": True, "pollData": updated_poll}


# Socket.IO events
@sio.event
async def connect(sid, environ):
    print(f"[Socket.IO] Client connected: {sid}")


@sio.event
async def disconnect(sid):
    print(f"[Socket.IO] Client disconnected: {sid}")


@sio.on('join-poll')
async def on_join_poll(sid, poll_id):
    await sio.enter_room(sid, f"poll-{poll_id}")
    print(f"[Socket.IO] Socket {sid} joined poll room: poll-{poll_id}")


@sio.on('leave-poll')
async def on_leave_poll(sid, poll_id):
    await sio.leave_room(sid, f"poll-{poll_id}")
    print(f"[Socket.IO] Socket {sid} left poll room: poll-{poll_id}")


# Entry point for uvicorn: main:sio_app