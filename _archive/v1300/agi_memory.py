"""
YEDAN AGI - Memory System
Persistent memory for goals, state, and learning
"""
import sqlite3
import json
import os
from datetime import datetime
from agi_config import config

DB_PATH = "yedan_agi.db"

class AGIMemory:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        # Ensure GCP Auth is configured via centralized config
        config.validate()
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # ... (schema creation omitted for brevity, logic remains same) ...
        
        # Goals table
        c.execute('''CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY,
            goal TEXT NOT NULL,
            priority INTEGER DEFAULT 5,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Actions log
        c.execute('''CREATE TABLE IF NOT EXISTS actions (
            id INTEGER PRIMARY KEY,
            action_type TEXT NOT NULL,
            description TEXT,
            result TEXT,
            success INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Observations
        c.execute('''CREATE TABLE IF NOT EXISTS observations (
            id INTEGER PRIMARY KEY,
            source TEXT,
            data TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Learning notes
        c.execute('''CREATE TABLE IF NOT EXISTS learnings (
            id INTEGER PRIMARY KEY,
            insight TEXT,
            context TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # State (key-value store)
        c.execute('''CREATE TABLE IF NOT EXISTS state (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        conn.commit()
        conn.close()
        print("[MEMORY] Database initialized")
        
        # Try to connect to Firestore (Cloud Memory)
        self.firestore = None
        try:
            from google.cloud import firestore
            self.firestore = firestore.Client()
            print("[MEMORY] GCP Firestore: Connected (Cloud Memory Active)")
        except Exception as e:
            print(f"[MEMORY] Using Local SQLite (GCP Firestore not active: {e})")
    
    def set_state(self, key, value):
        """Store a state value"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO state (key, value, updated_at) 
                     VALUES (?, ?, ?)''', (key, json.dumps(value), datetime.now()))
        conn.commit()
        conn.close()
    
    def get_state(self, key, default=None):
        """Retrieve a state value"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT value FROM state WHERE key = ?', (key,))
        row = c.fetchone()
        conn.close()
        return json.loads(row[0]) if row else default
    
    def add_goal(self, goal, priority=5):
        """Add a new goal"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('INSERT INTO goals (goal, priority) VALUES (?, ?)', (goal, priority))
        conn.commit()
        conn.close()
    
    def get_active_goals(self):
        """Get all active goals sorted by priority"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT id, goal, priority FROM goals WHERE status = "active" ORDER BY priority DESC')
        goals = c.fetchall()
        conn.close()
        return [{"id": g[0], "goal": g[1], "priority": g[2]} for g in goals]
    
    def log_action(self, action_type, description, result=None, success=True):
        """Log an action taken"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT INTO actions (action_type, description, result, success) 
                     VALUES (?, ?, ?, ?)''', (action_type, description, result, 1 if success else 0))
        conn.commit()
        conn.close()
    
    def log_observation(self, source, data):
        """Log an observation"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('INSERT INTO observations (source, data) VALUES (?, ?)', 
                  (source, json.dumps(data) if isinstance(data, dict) else str(data)))
        conn.commit()
        conn.close()
    
    def add_learning(self, insight, context=None):
        """Record a learning/insight"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('INSERT INTO learnings (insight, context) VALUES (?, ?)', (insight, context))
        conn.commit()
        conn.close()
    
    def get_recent_actions(self, limit=10):
        """Get recent actions"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT action_type, description, result, success, timestamp FROM actions ORDER BY timestamp DESC LIMIT ?', (limit,))
        actions = c.fetchall()
        conn.close()
        return [{"type": a[0], "description": a[1], "result": a[2], "success": bool(a[3]), "time": a[4]} for a in actions]
    
    def get_context_summary(self):
        """Get a summary of current context for AI reasoning"""
        goals = self.get_active_goals()
        recent = self.get_recent_actions(5)
        cycle = self.get_state("cycle_count", 0)
        
        return {
            "goals": goals,
            "recent_actions": recent,
            "cycle_count": cycle,
            "last_run": self.get_state("last_run", "Never")
        }

if __name__ == "__main__":
    # Test
    mem = AGIMemory()
    mem.add_goal("Generate revenue through AI intelligence reports", priority=10)
    mem.add_goal("Build Telegram subscriber base", priority=8)
    mem.add_goal("Monitor crypto market for opportunities", priority=7)
    print("[TEST] Goals:", mem.get_active_goals())
    print("[TEST] Context:", mem.get_context_summary())
