import sqlite3
import time
from pathlib import Path

_DB_PATH = Path(__file__).parent.parent / "rate_limit.db"
_WINDOW_SECONDS = 24 * 60 * 60  # 24-hour rolling window
_MAX_QUERIES = 5


class RateLimiter:
    """SQLite-backed rolling-window rate limiter.

    Persists usage counts across page refreshes for the same user_key.
    """

    def __init__(self, db_path: str = str(_DB_PATH)):
        self._db_path = db_path
        self._init_db()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _init_db(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS usage (
                    user_key  TEXT  NOT NULL,
                    timestamp REAL  NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_user_key ON usage (user_key)"
            )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path, check_same_thread=False)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _purge_expired(self, conn: sqlite3.Connection, user_key: str):
        cutoff = time.time() - _WINDOW_SECONDS
        conn.execute(
            "DELETE FROM usage WHERE user_key = ? AND timestamp < ?",
            (user_key, cutoff),
        )

    def _active_count(self, conn: sqlite3.Connection, user_key: str) -> int:
        cursor = conn.execute(
            "SELECT COUNT(*) FROM usage WHERE user_key = ?",
            (user_key,),
        )
        return cursor.fetchone()[0]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_allowed(self, user_key: str) -> bool:
        """Return True if the user has not yet exhausted their daily quota."""
        with self._connect() as conn:
            self._purge_expired(conn, user_key)
            return self._active_count(conn, user_key) < _MAX_QUERIES

    def increment_counter(self, user_key: str):
        """Record one successful API call for *user_key* at the current time."""
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO usage (user_key, timestamp) VALUES (?, ?)",
                (user_key, time.time()),
            )

    def remaining(self, user_key: str) -> int:
        """Return how many queries *user_key* can still make today."""
        with self._connect() as conn:
            self._purge_expired(conn, user_key)
            used = self._active_count(conn, user_key)
        return max(0, _MAX_QUERIES - used)
