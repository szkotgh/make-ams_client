import sqlite3
import config

## init db
class LogManager:
    def __init__(self):
        self.conn = sqlite3.connect(config.LOG_DB_PATH)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS main (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time DATETIME DEFAULT CURRENT_TIMESTAMP,
                method TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT
            )
        ''')
        self.conn.commit()
    
    def insert_log(self, method, action, details=None):
        self.cursor.execute('''
            INSERT INTO main (method, action, details)
            VALUES (?, ?, ?)
        ''', (method, action, details))
        self.conn.commit()
        
    def get_logs(self, limit=100):
        self.cursor.execute('''
            SELECT * FROM main
            ORDER BY time ASC
            LIMIT ?
        ''', (limit,))
        return self.cursor.fetchall()
    
    def log_close(self):
        self.conn.close()
        
service = LogManager()