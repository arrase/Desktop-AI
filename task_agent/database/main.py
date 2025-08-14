import sqlite3
from pathlib import Path
from typing import List, Optional, Sequence, Tuple, Any


class DatabaseManager:
    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db_path = Path(db_path) if db_path else Path.home() / ".config" / "JulesTask" / "tasks.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.create_table()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _execute(self, sql: str, params: Sequence[Any] = (), fetch: bool = False, commit: bool = False):
        """Run a query and optionally fetch results or commit.

        Centralizes error handling to reduce repetition.
        """
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                cur.execute(sql, params)
                if commit:
                    conn.commit()
                if fetch:
                    return cur.fetchall()
                return None
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return [] if fetch else None

    def create_table(self) -> None:
        self._execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                frequency TEXT NOT NULL
            )
            """,
            commit=True,
        )

    def add_task(self, description: str, frequency: str) -> Optional[int]:
        result = self._execute(
            "INSERT INTO tasks (description, frequency) VALUES (?, ?)",
            (description, frequency),
            commit=True,
        )

        # sqlite's cursor.lastrowid isn't returned by _execute, so open a short connection
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                cur.execute("SELECT last_insert_rowid()")
                row = cur.fetchone()
                return int(row[0]) if row else None
        except sqlite3.Error:
            return None

    def get_all_tasks(self) -> List[Tuple[int, str, str]]:
        rows = self._execute("SELECT id, description, frequency FROM tasks", fetch=True)
        return rows or []

    def delete_task(self, task_id: int) -> None:
        self._execute("DELETE FROM tasks WHERE id = ?", (task_id,), commit=True)
