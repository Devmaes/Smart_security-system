"""SQLite repository; private events stay in runtime/, never committed."""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
import csv
from pathlib import Path
import sqlite3
import threading
from collections.abc import Iterator


@dataclass(frozen=True, slots=True)
class User:
    user_id: str
    name: str
    role: str
    active: bool = True


@dataclass(frozen=True, slots=True)
class DetectionEvent:
    event_id: int
    occurred_at: str
    label: str
    user_id: str | None
    distance: float | None
    status: str


class Repository:
    """Simple thread-safe connection-per-operation storage for an operator PC."""

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._init_schema()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        with self._lock:
            conn = sqlite3.connect(str(self.db_path), timeout=10)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
                conn.commit()
            finally:
                conn.close()

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript('''
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    occurred_at TEXT NOT NULL,
                    label TEXT NOT NULL,
                    user_id TEXT,
                    distance REAL,
                    status TEXT NOT NULL CHECK(status IN ('recognized','unknown','reviewed','alert'))
                );
                CREATE INDEX IF NOT EXISTS idx_events_time ON events(occurred_at);
            ''')

    def add_user(self, user: User) -> None:
        uid, name, role = user.user_id.strip(), user.name.strip(), user.role.strip()
        if not uid or not name or not role or len(uid) > 64 or len(name) > 120:
            raise ValueError('Identifiant, nom et rôle sont obligatoires')
        with self._connect() as conn:
            conn.execute(
                'INSERT INTO users(user_id,name,role,active,created_at) VALUES (?,?,?,?,?)',
                (uid, name, role, int(user.active), datetime.now(timezone.utc).isoformat()),
            )

    def list_users(self, query: str = '') -> list[User]:
        with self._connect() as conn:
            rows = conn.execute(
                'SELECT user_id,name,role,active FROM users WHERE lower(name) LIKE ? OR lower(user_id) LIKE ? ORDER BY name',
                (f'%{query.lower()}%', f'%{query.lower()}%'),
            ).fetchall()
        return [User(r['user_id'], r['name'], r['role'], bool(r['active'])) for r in rows]

    def delete_user(self, user_id: str) -> None:
        with self._connect() as conn:
            conn.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
        # Existing logs retain the pseudonymous ID for audit; no biometric template removed here.
        # Call FaceEngine.remove_template when deleting the enrollment as well.

    def log(self, label: str, user_id: str | None, distance: float | None, status: str) -> None:
        if status not in ('recognized', 'unknown', 'reviewed', 'alert'):
            raise ValueError('Statut invalide')
        with self._connect() as conn:
            conn.execute(
                'INSERT INTO events(occurred_at,label,user_id,distance,status) VALUES (?,?,?,?,?)',
                (datetime.now(timezone.utc).isoformat(timespec='seconds'), label, user_id, distance, status),
            )

    def list_events(self, limit: int = 200, status: str | None = None) -> list[DetectionEvent]:
        with self._connect() as conn:
            if status:
                rows = conn.execute(
                    'SELECT * FROM events WHERE status=? ORDER BY event_id DESC LIMIT ?',
                    (status, limit),
                ).fetchall()
            else:
                rows = conn.execute('SELECT * FROM events ORDER BY event_id DESC LIMIT ?', (limit,)).fetchall()
        return [DetectionEvent(**dict(r)) for r in rows]

    def mark_alert(self, event_id: int) -> None:
        with self._connect() as conn:
            conn.execute("UPDATE events SET status='alert' WHERE event_id=? AND status IN ('unknown','reviewed')", (event_id,))

    def statistics(self) -> dict[str, int]:
        with self._connect() as conn:
            registered = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
            counts = {r['status']: r['count'] for r in conn.execute(
                'SELECT status, COUNT(*) AS count FROM events GROUP BY status'
            )}
        return {
            'users': registered,
            'recognized': counts.get('recognized', 0),
            'unknown': counts.get('unknown', 0),
            'alert': counts.get('alert', 0),
            'total': sum(counts.values()),
        }

    def export_csv(self, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        def safe(x: object) -> str:
            value = '' if x is None else str(x)
            return "'" + value if value.startswith(('=', '+', '-', '@', '\t', '\r')) else value
        with destination.open('w', newline='', encoding='utf-8-sig') as fp:
            writer = csv.writer(fp)
            writer.writerow(['Date UTC', 'Identité affichée', 'ID', 'Distance', 'Statut'])
            for event in reversed(self.list_events(limit=100000)):
                writer.writerow([safe(event.occurred_at), safe(event.label), safe(event.user_id),
                                 safe(event.distance), safe(event.status)])
