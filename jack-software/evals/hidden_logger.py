# NOTE: Not a great implementation that follows all my intended patterns, but good enough
# because I found some issues that I want to iterate on.
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from functools import cached_property


@dataclass
class EvalRunResult:
    """Represents a single eval run result to be logged."""

    wall_clock_time: float
    input_tokens: int
    output_tokens: int
    eval_results: dict
    git_revision: str
    git_diff: str
    working_directory: str
    timestamp: datetime
    model: str


@dataclass
class LogQueryResult:
    """Represents a result from querying logged eval runs."""

    id: int
    wall_clock_time: float
    input_tokens: int
    output_tokens: int
    eval_results: dict
    git_revision: str
    git_diff: str
    working_directory: str
    timestamp: datetime
    model: str


class Logger:
    """Service for logging and retrieving eval run results in SQLite.

    This logger stores evaluation metrics and metadata in a SQLite database,
    allowing for tracking and analysis of eval runs over time.
    """

    def __init__(self, db_path: str | None = None) -> None:
        """Initialize the logger with optional database path.

        Args:
            db_path: Path to SQLite database file. Defaults to evals.db in current directory.

        No side effects - database is initialized lazily on first use.
        """
        self._db_path = db_path or "evals.db"

    @cached_property
    def _connection(self) -> sqlite3.Connection:
        """Lazy initialization of database connection."""
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        self._initialize_schema(conn)
        return conn

    def _initialize_schema(self, conn: sqlite3.Connection) -> None:
        """Create the eval runs table if it doesn't exist."""
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS eval_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wall_clock_time REAL NOT NULL,
                input_tokens INTEGER NOT NULL,
                output_tokens INTEGER NOT NULL,
                eval_results TEXT NOT NULL,
                git_revision TEXT NOT NULL,
                git_diff TEXT NOT NULL,
                working_directory TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                model TEXT NOT NULL DEFAULT 'claude-haiku-4-5-20251001'
            )
        """)
        conn.commit()
        self._migrate_schema(conn)

    def _migrate_schema(self, conn: sqlite3.Connection) -> None:
        """Apply schema migrations for existing databases."""
        cursor = conn.cursor()

        # Check if git_diff column exists
        cursor.execute("PRAGMA table_info(eval_runs)")
        columns = {row[1] for row in cursor.fetchall()}

        # Add git_diff column if it doesn't exist
        if "git_diff" not in columns:
            cursor.execute(
                "ALTER TABLE eval_runs ADD COLUMN git_diff TEXT NOT NULL DEFAULT ''"
            )
            conn.commit()

        # Add model column if it doesn't exist
        cursor.execute("PRAGMA table_info(eval_runs)")
        columns = {row[1] for row in cursor.fetchall()}

        if "model" not in columns:
            cursor.execute(
                "ALTER TABLE eval_runs ADD COLUMN model TEXT NOT NULL DEFAULT 'claude-haiku-4-5-20251001'"
            )
            conn.commit()

    def log_eval_run(self, result: EvalRunResult) -> int:
        """Log an eval run result to the database.

        Args:
            result: EvalRunResult containing all metrics and metadata

        Returns:
            The ID of the inserted row

        Raises:
            sqlite3.Error: If database operation fails
        """
        cursor = self._connection.cursor()

        eval_results_json = json.dumps(result.eval_results)
        timestamp_str = result.timestamp.isoformat()

        cursor.execute(
            """
            INSERT INTO eval_runs
            (wall_clock_time, input_tokens, output_tokens, eval_results, git_revision, git_diff, working_directory, timestamp, model)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                result.wall_clock_time,
                result.input_tokens,
                result.output_tokens,
                eval_results_json,
                result.git_revision,
                result.git_diff,
                result.working_directory,
                timestamp_str,
                result.model,
            ),
        )

        self._connection.commit()
        return cursor.lastrowid

    def get_eval_run(self, run_id: int) -> LogQueryResult | None:
        """Retrieve a specific eval run by ID.

        Args:
            run_id: The ID of the eval run to retrieve

        Returns:
            LogQueryResult if found, None otherwise

        Raises:
            sqlite3.Error: If database operation fails
        """
        cursor = self._connection.cursor()
        cursor.execute(
            """
            SELECT * FROM eval_runs WHERE id = ?
        """,
            (run_id,),
        )

        row = cursor.fetchone()
        if not row:
            return None

        return self._row_to_result(row)

    def get_all_eval_runs(self) -> list[LogQueryResult]:
        """Retrieve all logged eval runs.

        Returns:
            List of all LogQueryResult records

        Raises:
            sqlite3.Error: If database operation fails
        """
        cursor = self._connection.cursor()
        cursor.execute("SELECT * FROM eval_runs ORDER BY id DESC")

        return [self._row_to_result(row) for row in cursor.fetchall()]

    def get_eval_runs_by_revision(self, git_revision: str) -> list[LogQueryResult]:
        """Retrieve all eval runs for a specific git revision.

        Args:
            git_revision: The git commit hash or jj revision identifier

        Returns:
            List of LogQueryResult records for the given revision

        Raises:
            sqlite3.Error: If database operation fails
        """
        cursor = self._connection.cursor()
        cursor.execute(
            """
            SELECT * FROM eval_runs WHERE git_revision = ? ORDER BY timestamp DESC
        """,
            (git_revision,),
        )

        return [self._row_to_result(row) for row in cursor.fetchall()]

    def delete_eval_run(self, run_id: int) -> bool:
        """Delete an eval run record by ID.

        Args:
            run_id: The ID of the eval run to delete

        Returns:
            True if a record was deleted, False if not found

        Raises:
            sqlite3.Error: If database operation fails
        """
        cursor = self._connection.cursor()
        cursor.execute("DELETE FROM eval_runs WHERE id = ?", (run_id,))
        self._connection.commit()

        return cursor.rowcount > 0

    def clear_all_runs(self) -> int:
        """Delete all eval run records from the database.

        Returns:
            Number of records deleted

        Raises:
            sqlite3.Error: If database operation fails
        """
        cursor = self._connection.cursor()
        cursor.execute("DELETE FROM eval_runs")
        self._connection.commit()

        return cursor.rowcount

    def _row_to_result(self, row: sqlite3.Row) -> LogQueryResult:
        """Convert a database row to a LogQueryResult object.

        Args:
            row: A sqlite3.Row from a query result

        Returns:
            Parsed LogQueryResult with deserialized eval_results
        """
        eval_results = json.loads(row["eval_results"])
        timestamp = datetime.fromisoformat(row["timestamp"])

        return LogQueryResult(
            id=row["id"],
            wall_clock_time=row["wall_clock_time"],
            input_tokens=row["input_tokens"],
            output_tokens=row["output_tokens"],
            eval_results=eval_results,
            git_revision=row["git_revision"],
            git_diff=row["git_diff"],
            working_directory=row["working_directory"],
            timestamp=timestamp,
            model=row["model"],
        )

    def close(self) -> None:
        """Close the database connection if it was initialized."""
        if "connection" in self.__dict__:
            self._connection.close()


if __name__ == "__main__":
    logger = Logger("evals.db")

    print(logger.get_all_eval_runs())
