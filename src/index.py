import sqlite3
import os


class FingerprintIndex:
    def __init__(self, db_path="data/fingerprints.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True) if os.path.dirname(db_path) else None
        self.conn = sqlite3.connect(db_path)
        self._setup()

    def _setup(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS fingerprints (
                hash INTEGER NOT NULL,
                track_id TEXT NOT NULL,
                offset_time INTEGER NOT NULL
            )
        """)
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_hash ON fingerprints(hash)"
        )
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS tracks (
                track_id TEXT PRIMARY KEY,
                title TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def add_track(self, track_id, hashes, title=None):
        # register track metadata (idempotent)
        self.conn.execute(
            "INSERT OR IGNORE INTO tracks (track_id, title) VALUES (?, ?)",
            (track_id, title or track_id)
        )
        # bulk insert fingerprints
        self.conn.executemany(
            "INSERT INTO fingerprints (hash, track_id, offset_time) VALUES (?, ?, ?)",
            [(int(h), track_id, int(t)) for h, t in hashes]
        )
        self.conn.commit()

    def lookup(self, h):
        """Single-hash lookup (kept for compatibility)."""
        cur = self.conn.execute(
            "SELECT track_id, offset_time FROM fingerprints WHERE hash = ?",
            (int(h),)
        )
        return cur.fetchall()

    def lookup_batch(self, hash_list):
        """
        Batch lookup - much faster than looping lookup() per hash.
        Returns: { hash: [(track_id, offset_time), ...], ... }
        """
        if not hash_list:
            return {}

        results = {h: [] for h in hash_list}
        # SQLite has a default limit of 999 params per query - chunk it
        CHUNK = 900
        unique_hashes = list(set(int(h) for h in hash_list))

        for i in range(0, len(unique_hashes), CHUNK):
            chunk = unique_hashes[i:i + CHUNK]
            placeholders = ",".join("?" * len(chunk))
            cur = self.conn.execute(
                f"SELECT hash, track_id, offset_time FROM fingerprints WHERE hash IN ({placeholders})",
                chunk
            )
            for h, track_id, offset_time in cur.fetchall():
                results[h].append((track_id, offset_time))

        return results

    def track_exists(self, track_id):
        cur = self.conn.execute(
            "SELECT 1 FROM tracks WHERE track_id = ?", (track_id,)
        )
        return cur.fetchone() is not None

    def __len__(self):
        return self.conn.execute(
            "SELECT COUNT(DISTINCT hash) FROM fingerprints"
        ).fetchone()[0]

    def close(self):
        self.conn.close()