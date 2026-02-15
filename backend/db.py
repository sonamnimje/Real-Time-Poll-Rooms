import os
import sqlite3
from typing import List, Dict, Optional

DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "polls.db"))

_conn = sqlite3.connect(DB_PATH, check_same_thread=False)
_conn.row_factory = sqlite3.Row
_conn.execute("PRAGMA foreign_keys = ON")

_conn.executescript(
    """
    CREATE TABLE IF NOT EXISTS polls (
        id TEXT PRIMARY KEY,
        question TEXT NOT NULL,
        created_at INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS options (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        poll_id TEXT NOT NULL,
        text TEXT NOT NULL,
        FOREIGN KEY (poll_id) REFERENCES polls(id) ON DELETE CASCADE
    );

    -- votes table will be (re)created/migrated below to remove per-IP uniqueness
    """
)


def _ensure_votes_table():
    """Create or migrate votes table to allow multiple votes per IP while keeping per-voter uniqueness."""
    create_sql = """
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            poll_id TEXT NOT NULL,
            option_id INTEGER NOT NULL,
            voter_identifier TEXT NOT NULL,
            ip_address TEXT NOT NULL,
            voted_at INTEGER NOT NULL,
            FOREIGN KEY (poll_id) REFERENCES polls(id) ON DELETE CASCADE,
            FOREIGN KEY (option_id) REFERENCES options(id) ON DELETE CASCADE,
            UNIQUE(poll_id, voter_identifier)
        );
    """

    existing = _conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='votes'"
    ).fetchone()

    # No table yet: create it fresh
    if not existing:
        _conn.executescript(create_sql)
    else:
        sql_text = existing[0] or ""
        if "UNIQUE(poll_id, ip_address)" in sql_text:
            # Migrate: rebuild table without IP uniqueness
            with _conn:
                _conn.executescript(
                    """
                    CREATE TABLE votes_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        poll_id TEXT NOT NULL,
                        option_id INTEGER NOT NULL,
                        voter_identifier TEXT NOT NULL,
                        ip_address TEXT NOT NULL,
                        voted_at INTEGER NOT NULL,
                        FOREIGN KEY (poll_id) REFERENCES polls(id) ON DELETE CASCADE,
                        FOREIGN KEY (option_id) REFERENCES options(id) ON DELETE CASCADE,
                        UNIQUE(poll_id, voter_identifier)
                    );

                    INSERT INTO votes_new (id, poll_id, option_id, voter_identifier, ip_address, voted_at)
                    SELECT id, poll_id, option_id, voter_identifier, ip_address, voted_at FROM votes;

                    DROP TABLE votes;
                    ALTER TABLE votes_new RENAME TO votes;
                    """
                )

    # Ensure indexes
    _conn.executescript(
        """
        CREATE INDEX IF NOT EXISTS idx_votes_poll ON votes(poll_id);
        CREATE INDEX IF NOT EXISTS idx_options_poll ON options(poll_id);
        """
    )


_ensure_votes_table()


def create_poll(poll_id: str, question: str, options: List[str]) -> str:
    with _conn:
        _conn.execute(
            "INSERT INTO polls (id, question, created_at) VALUES (?, ?, strftime('%s','now')*1000)",
            (poll_id, question),
        )
        _conn.executemany(
            "INSERT INTO options (poll_id, text) VALUES (?, ?)",
            [(poll_id, opt) for opt in options],
        )
    return poll_id


def _get_vote_map(poll_id: str) -> Dict[int, int]:
    rows = _conn.execute(
        "SELECT option_id, COUNT(*) as count FROM votes WHERE poll_id = ? GROUP BY option_id",
        (poll_id,),
    ).fetchall()
    return {row["option_id"]: row["count"] for row in rows}


def get_poll_data(poll_id: str) -> Optional[Dict]:
    poll = _conn.execute("SELECT * FROM polls WHERE id = ?", (poll_id,)).fetchone()
    if not poll:
        return None

    options = _conn.execute("SELECT * FROM options WHERE poll_id = ?", (poll_id,)).fetchall()
    vote_map = _get_vote_map(poll_id)
    total_votes_row = _conn.execute("SELECT COUNT(*) as total FROM votes WHERE poll_id = ?", (poll_id,)).fetchone()
    total_votes = total_votes_row["total"] if total_votes_row else 0

    options_with_votes = [
        {"id": opt["id"], "text": opt["text"], "votes": vote_map.get(opt["id"], 0)}
        for opt in options
    ]

    return {
        "id": poll["id"],
        "question": poll["question"],
        "options": options_with_votes,
        "totalVotes": total_votes,
    }


def has_user_voted(poll_id: str, voter_identifier: str, ip_address: str) -> bool:
    # Allow multiple votes from the same IP; only block by voter_identifier
    row = _conn.execute(
        "SELECT 1 FROM votes WHERE poll_id = ? AND voter_identifier = ?",
        (poll_id, voter_identifier),
    ).fetchone()
    return bool(row)


def cast_vote(poll_id: str, option_id: int, voter_identifier: str, ip_address: str) -> bool:
    try:
        with _conn:
            _conn.execute(
                "INSERT INTO votes (poll_id, option_id, voter_identifier, ip_address, voted_at) VALUES (?, ?, ?, ?, strftime('%s','now')*1000)",
                (poll_id, option_id, voter_identifier, ip_address),
            )
        return True
    except sqlite3.IntegrityError:
        return False
