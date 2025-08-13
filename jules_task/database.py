import sqlite3
from pathlib import Path


class DatabaseManager:
    def __init__(self, db_path=None):
        if db_path:
            self.db_path = Path(db_path)
        else:
            self.db_path = Path.home() / ".config" / "JulesTask" / "tasks.db"

        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.create_table()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def create_table(self):
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        description TEXT NOT NULL,
                        frequency TEXT NOT NULL
                    )
                """
                )
                conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")

    def add_task(self, description, frequency):
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO tasks (description, frequency) VALUES (?, ?)",
                    (description, frequency),
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Failed to add task: {e}")
            return None

    def get_all_tasks(self):
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, description, frequency FROM tasks")
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Failed to get tasks: {e}")
            return []

    def delete_task(self, task_id):
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Failed to delete task: {e}")
