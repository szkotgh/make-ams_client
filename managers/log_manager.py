import sqlite3
import setting

class LogManager:
    def __init__(self):
        self.conn = sqlite3.connect(setting.LOG_DB_PATH, isolation_level=None, check_same_thread=False)
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
            # Use existing connection to prevent creating new connections
            cursor = self.cursor
            cursor.execute('''
                INSERT INTO main (method, action, details)
                VALUES (?, ?, ?)
            ''', (method, action, details))
            self.conn.commit()
        except sqlite3.OperationalError as e:
            print("Failed to write log:", e)
            # Try to reconnect on connection error
            try:
                self.conn.close()
                self.conn = sqlite3.connect(setting.LOG_DB_PATH, isolation_level=None, check_same_thread=False)
                self.cursor = self.conn.cursor()
                self.cursor.execute('PRAGMA journal_mode=WAL;')
            except Exception as reconnect_error:
                print(f"Failed to reconnect to database: {reconnect_error}")

    def get_logs(self, limit=100):
        self.cursor.execute('''
            SELECT * FROM main
            ORDER BY time DESC
            LIMIT ?
        ''', (limit,))
        return self.cursor.fetchall()

    def log_close(self, *_):
        self.conn.commit()
        self.conn.close()

    def __enter__(self):
        return self
    
    def __exit__(self, *_):
        self.log_close()

service = LogManager()