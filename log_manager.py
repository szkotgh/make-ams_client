import sqlite3
import config

class LogManager:
    def __init__(self):
        self.conn = sqlite3.connect(config.LOG_DB_PATH, isolation_level=None)
        self.cursor = self.conn.cursor()

        self.cursor.execute('PRAGMA journal_mode=WAL;')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS main (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time DATETIME DEFAULT (datetime('now', 'localtime')),
                method TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT
            )
        ''')
        self.conn.commit()

    def insert_log(self, method, action, details=None):
        try:
            self.cursor.execute('''
                INSERT INTO main (method, action, details)
                VALUES (?, ?, ?)
            ''', (method, action, details))
            self.conn.commit()
        except sqlite3.OperationalError as e:
            print("Failed to write log:", e)

    def get_logs(self, limit=100):
        self.cursor.execute('''
            SELECT * FROM main
            ORDER BY time ASC
            LIMIT ?
        ''', (limit,))
        return self.cursor.fetchall()

    def log_close(self):
        self.conn.commit()
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.log_close()

service = LogManager()