import sqlite3
from pathlib import Path

class DatabaseManager:
    def __init__(self, db_path=None):
        if db_path:
            self.db_path = Path(db_path)
        else:
            self.db_path = Path.home() / ".config" / "JulesTask" / "tasks.db"

        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.db_path)
        self.create_table()

    def create_table(self):
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                frequency TEXT NOT NULL
            )
        """)
        self.connection.commit()

    def add_task(self, description, frequency):
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO tasks (description, frequency) VALUES (?, ?)",
            (description, frequency),
        )
        self.connection.commit()
        return cursor.lastrowid

    def get_all_tasks(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, description, frequency FROM tasks")
        return cursor.fetchall()

    def delete_task(self, task_id):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.connection.commit()

    def close(self):
        self.create_table()

    def create_table(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT NOT NULL,
                    frequency TEXT NOT NULL
                )
            """)
            conn.commit()

    def add_task(self, description, frequency):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tasks (description, frequency) VALUES (?, ?)",
                (description, frequency),
            )
            conn.commit()
            return cursor.lastrowid

    def get_all_tasks(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, description, frequency FROM tasks")
            return cursor.fetchall()

    def delete_task(self, task_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
