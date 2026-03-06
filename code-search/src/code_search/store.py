"""SQLite storage for code chunks and embeddings."""

import hashlib
import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path

import numpy as np

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    file_mtime REAL NOT NULL,
    chunk_type TEXT NOT NULL,
    chunk_name TEXT NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    source_code TEXT NOT NULL,
    description TEXT,
    embedding BLOB NOT NULL,
    created_at REAL DEFAULT (unixepoch('now'))
);
CREATE INDEX IF NOT EXISTS idx_chunks_file ON chunks(file_path);
CREATE INDEX IF NOT EXISTS idx_chunks_mtime ON chunks(file_path, file_mtime);
"""


@dataclass(frozen=True)
class StoredChunk:
    id: int
    file_path: str
    file_mtime: float
    chunk_type: str
    chunk_name: str
    start_line: int
    end_line: int
    source_code: str
    description: str | None
    embedding: np.ndarray


def _db_path_for_project(project_root: str) -> Path:
    """Compute per-project DB path: ~/.claude/code-search/{hash}.db"""
    project_hash = hashlib.sha256(project_root.encode()).hexdigest()[:16]
    db_dir = Path.home() / ".claude" / "code-search"
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir / f"{project_hash}.db"


class CodeSearchStore:
    def __init__(self, project_root: str | None = None):
        if project_root is None:
            project_root = os.getcwd()
        self._project_root = os.path.abspath(project_root)
        self._db_path = _db_path_for_project(self._project_root)
        self._conn = sqlite3.connect(str(self._db_path))
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA synchronous=NORMAL")
        self._conn.executescript(SCHEMA_SQL)
        self._conn.commit()

    def get_file_mtime(self, file_path: str) -> float | None:
        """Get stored mtime for a file. Returns None if not indexed."""
        row = self._conn.execute(
            "SELECT file_mtime FROM chunks WHERE file_path = ? LIMIT 1",
            (file_path,),
        ).fetchone()
        return row[0] if row else None

    def delete_file_chunks(self, file_path: str) -> int:
        """Delete all chunks for a file. Returns count deleted."""
        cursor = self._conn.execute(
            "DELETE FROM chunks WHERE file_path = ?", (file_path,)
        )
        self._conn.commit()
        return cursor.rowcount

    def insert_chunk(
        self,
        file_path: str,
        file_mtime: float,
        chunk_type: str,
        chunk_name: str,
        start_line: int,
        end_line: int,
        source_code: str,
        embedding: np.ndarray,
        description: str | None = None,
    ) -> int:
        """Insert a chunk and return its id."""
        cursor = self._conn.execute(
            """INSERT INTO chunks
               (file_path, file_mtime, chunk_type, chunk_name,
                start_line, end_line, source_code, description, embedding)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                file_path,
                file_mtime,
                chunk_type,
                chunk_name,
                start_line,
                end_line,
                source_code,
                description,
                embedding.astype(np.float32).tobytes(),
            ),
        )
        self._conn.commit()
        return cursor.lastrowid

    def get_all_chunks(self) -> list[StoredChunk]:
        """Load all chunks with their embeddings."""
        rows = self._conn.execute(
            """SELECT id, file_path, file_mtime, chunk_type, chunk_name,
                      start_line, end_line, source_code, description, embedding
               FROM chunks"""
        ).fetchall()
        return [
            StoredChunk(
                id=row[0],
                file_path=row[1],
                file_mtime=row[2],
                chunk_type=row[3],
                chunk_name=row[4],
                start_line=row[5],
                end_line=row[6],
                source_code=row[7],
                description=row[8],
                embedding=np.frombuffer(row[9], dtype=np.float32),
            )
            for row in rows
        ]

    def update_description(self, chunk_id: int, description: str) -> None:
        """Update the description for a chunk."""
        self._conn.execute(
            "UPDATE chunks SET description = ? WHERE id = ?",
            (description, chunk_id),
        )
        self._conn.commit()

    def get_stats(self) -> dict:
        """Get index statistics."""
        row = self._conn.execute(
            "SELECT COUNT(*), COUNT(DISTINCT file_path) FROM chunks"
        ).fetchone()
        return {
            "total_chunks": row[0],
            "total_files": row[1],
            "db_path": str(self._db_path),
        }

    def close(self) -> None:
        self._conn.close()
