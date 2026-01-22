# storage.py

import sqlite3
import config
import threading

class Storage:
    """
    Handles persistent storage for the offline mesh map.
    Uses SQLite for annotations, obstacles, peers, and seen messages.
    Thread-safe for concurrent access.
    """

    def __init__(self, db_file=None):
        self.db_file = db_file if db_file else config.DB_FILE
        self.lock = threading.Lock()
        self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        print(f"[Storage] Connecting to DB: {self.db_file}")
        self._initialize_db()

    def _initialize_db(self):
        """
        Create tables if they do not exist.
        """
        with self.lock:
            cursor = self.conn.cursor()

            # Annotations table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS annotations (
                id TEXT PRIMARY KEY,
                peer_id TEXT,
                timestamp INTEGER,
                lat REAL,
                lon REAL,
                data TEXT
            )
            """)

            # Obstacles table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS obstacles (
                id TEXT PRIMARY KEY,
                peer_id TEXT,
                timestamp INTEGER,
                lat REAL,
                lon REAL,
                radius REAL,
                data TEXT
            )
            """)

            # Peers table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS peers (
                peer_id TEXT PRIMARY KEY,
                last_seen INTEGER
            )
            """)

            # Messages seen (for mesh deduplication)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages_seen (
                msg_id TEXT PRIMARY KEY,
                timestamp INTEGER
            )
            """)

            self.conn.commit()
            print("[Storage] Tables initialized successfully")

    # -----------------------------
    # Annotations
    # -----------------------------
    def add_annotation(self, annotation):
        """
        Add an annotation to the database.
        annotation: dict with keys 'id', 'peer_id', 'timestamp', 'lat', 'lon', 'data'
        """
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute("""
            INSERT OR IGNORE INTO annotations (id, peer_id, timestamp, lat, lon, data)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                annotation['id'],
                annotation['peer_id'],
                annotation['timestamp'],
                annotation['lat'],
                annotation['lon'],
                annotation.get('data', '')
            ))
            self.conn.commit()
            print(f"[Storage] Added annotation {annotation['id']} at ({annotation['lat']}, {annotation['lon']})")

    def get_all_annotations(self):
        """Return a list of all annotations as dicts."""
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM annotations")
            rows = cursor.fetchall()
            print(f"[Storage] Fetched {len(rows)} annotations")
            return [dict(row) for row in rows]

    # -----------------------------
    # Obstacles
    # -----------------------------
    def add_obstacle(self, obstacle):
        """
        Add an obstacle to the database.
        obstacle: dict with keys 'id', 'peer_id', 'timestamp', 'lat', 'lon', 'radius', 'data'
        """
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute("""
            INSERT OR IGNORE INTO obstacles (id, peer_id, timestamp, lat, lon, radius, data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                obstacle['id'],
                obstacle['peer_id'],
                obstacle['timestamp'],
                obstacle['lat'],
                obstacle['lon'],
                obstacle.get('radius', 1.0),
                obstacle.get('data', '')
            ))
            self.conn.commit()
            print(f"[Storage] Added obstacle {obstacle['id']} at ({obstacle['lat']}, {obstacle['lon']})")

    def get_all_obstacles(self):
        """Return a list of all obstacles as dicts."""
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM obstacles")
            rows = cursor.fetchall()
            print(f"[Storage] Fetched {len(rows)} obstacles")
            return [dict(row) for row in rows]

    # -----------------------------
    # Peers
    # -----------------------------
    def update_peer(self, peer_id, last_seen=None):
        """Insert or update peer last_seen timestamp."""
        import time
        if last_seen is None:
            last_seen = int(time.time())
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute("""
            INSERT INTO peers (peer_id, last_seen)
            VALUES (?, ?)
            ON CONFLICT(peer_id) DO UPDATE SET last_seen=excluded.last_seen
            """, (peer_id, last_seen))
            self.conn.commit()
            print(f"[Storage] Updated peer {peer_id} last_seen {last_seen}")

    def get_peers(self):
        """Return all peers as dicts."""
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM peers")
            rows = cursor.fetchall()
            print(f"[Storage] Fetched {len(rows)} peers")
            return [dict(row) for row in rows]

    # -----------------------------
    # Messages Seen
    # -----------------------------
    def add_message_seen(self, msg_id, timestamp=None):
        """Mark a message ID as seen to prevent duplicate processing."""
        import time
        if timestamp is None:
            timestamp = int(time.time())
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute("""
            INSERT OR IGNORE INTO messages_seen (msg_id, timestamp)
            VALUES (?, ?)
            """, (msg_id, timestamp))
            self.conn.commit()
            print(f"[Storage] Message seen recorded: {msg_id}")

    def has_seen_message(self, msg_id):
        """Check if a message ID has already been processed."""
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute("SELECT 1 FROM messages_seen WHERE msg_id=?", (msg_id,))
            seen = cursor.fetchone() is not None
            print(f"[Storage] Has seen message {msg_id}? {seen}")
            return seen

    # -----------------------------
    # Close connection
    # -----------------------------
    def close(self):
        with self.lock:
            self.conn.close()
            print("[Storage] DB connection closed")
