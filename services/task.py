import sqlite3
from datetime import datetime

class Task:
    def __init__(self, id, title, description, created_at, due_date, 
                 base_priority, dynamic_priority, time_estimate, 
                 completed=False, completed_at=None):
        self.id = id
        self.title = title
        self.description = description
        self.created_at = created_at
        self.due_date = due_date
        self.base_priority = base_priority
        self.dynamic_priority = dynamic_priority
        self.time_estimate = time_estimate
        self.completed = completed
        self.completed_at = completed_at
    
    @classmethod
    def create(cls, conn, title, description, due_date, 
              base_priority, dynamic_priority, time_estimate):
        c = conn.cursor()
        c.execute(
            "INSERT INTO tasks (title, description, created_at, due_date, "
            "base_priority, dynamic_priority, time_estimate, completed) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (title, description, datetime.now(), due_date, 
             base_priority, dynamic_priority, time_estimate, False)
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