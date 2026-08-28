import psycopg2
import psycopg2.extras
import os


class FingerprintIndex:
    def __init__(self, db_url=None):
        self.db_url = db_url or os.environ.get("DATABASE_URL")
        if not self.db_url:
            raise ValueError("No database URL provided. Set DATABASE_URL env var or pass db_url.")
        self.conn = psycopg2.connect(self.db_url)
        self._setup()

    def _setup(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS fingerprints (
                    hash BIGINT NOT NULL,
                    track_id TEXT NOT NULL,
                    offset_time INTEGER NOT NULL
                )
            """)
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_hash ON fingerprints(hash)"
            )
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tracks (
                    track_id TEXT PRIMARY KEY,
                    title TEXT,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        self.conn.commit()

    def add_track(self, track_id, hashes, title=None):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO tracks (track_id, title) VALUES (%s, %s) ON CONFLICT (track_id) DO NOTHING",
                (track_id, title or track_id)
            )
            psycopg2.extras.execute_values(
                cur,
                "INSERT INTO fingerprints (hash, track_id, offset_time) VALUES %s",
                [(int(h), track_id, int(t)) for h, t in hashes]
            )
        self.conn.commit()

    def lookup(self, h):
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT track_id, offset_time FROM fingerprints WHERE hash = %s",
                (int(h),)
            )
            return cur.fetchall()

    def lookup_batch(self, hash_list):
        if not hash_list:
            return {}

        results = {h: [] for h in hash_list}
        unique_hashes = list(set(int(h) for h in hash_list))

        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT hash, track_id, offset_time FROM fingerprints WHERE hash = ANY(%s)",
                (unique_hashes,)
            )
            for h, track_id, offset_time in cur.fetchall():
                results[h].append((track_id, offset_time))

        return results

    def track_exists(self, track_id):
        with self.conn.cursor() as cur:
            cur.execute("SELECT 1 FROM tracks WHERE track_id = %s", (track_id,))
            return cur.fetchone() is not None

    def __len__(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(DISTINCT hash) FROM fingerprints")
            return cur.fetchone()[0]

    def close(self):
        self.conn.close()