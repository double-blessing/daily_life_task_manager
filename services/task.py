import sqlite3
from datetime import datetime

class Task:
    def __init__(self, id, title, description, created_at, due_date,
                 base_priority, dynamic_priority, energy_level, time_estimate,
                 completed=False, completed_at=None):
        self.id = id
        self.title = title
        self.description = description
        
        # Handle string-to-datetime conversion if necessary
        self.created_at = self._to_datetime(created_at)
        self.due_date = self._to_datetime(due_date)
        
        self.base_priority = base_priority
        self.dynamic_priority = dynamic_priority
        self.energy_level = energy_level 
        self.time_estimate = time_estimate
        self.completed = bool(completed)
        self.completed_at = self._to_datetime(completed_at)

    def _to_datetime(self, value):
        """Helper to convert string from DB to datetime object."""
        if isinstance(value, str):
            try:
                # This format handles the default SQLite timestamp format
                return datetime.fromisoformat(value.split('.')[0])
            except (ValueError, TypeError):
                return None
        return value

    @classmethod
    # --- 'energy_level' to the create method ---
    def create(cls, conn, title, description, due_date,
              base_priority, dynamic_priority, time_estimate, energy_level):
        c = conn.cursor()
        c.execute(
            "INSERT INTO tasks (title, description, created_at, due_date, "
            "base_priority, dynamic_priority, time_estimate, energy_level, completed) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (title, description, datetime.now(), due_date,
             base_priority, dynamic_priority, time_estimate, energy_level, False)
        )
        conn.commit()

    @classmethod
    def get_all(cls, conn):
        c = conn.cursor()
        c.execute("SELECT * FROM tasks ORDER BY dynamic_priority DESC")
        rows = c.fetchall()
        return [cls(*row) for row in rows]

    @classmethod
    def mark_complete(cls, conn, task_id):
        c = conn.cursor()
        c.execute(
            "UPDATE tasks SET completed = ?, completed_at = ? WHERE id = ?",
            (True, datetime.now(), task_id)
        )
        conn.commit()

    @classmethod
    def delete(cls, conn, task_id):
        c = conn.cursor()
        c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
