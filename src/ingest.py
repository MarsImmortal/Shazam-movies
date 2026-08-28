import argparse
import sys
import os
import tempfile

sys.path.append(os.path.dirname(__file__))

from extract_audio import extract_audio
from fingerprint import fingerprint
from index import FingerprintIndex


def generate_track_id(video_path):
    """Derive a simple track_id from the filename (no extension, no spaces)."""
    base = os.path.splitext(os.path.basename(video_path))[0]
    return base.lower().replace(" ", "_")


def ingest(video_path, title=None, track_id=None, db_path="data/fingerprints.db", force=False):
    if not os.path.exists(video_path):
        print(f"Error: file not found -> {video_path}")
        sys.exit(1)

    track_id = track_id or generate_track_id(video_path)
    title = title or track_id

    idx = FingerprintIndex(db_path)

    if idx.track_exists(track_id) and not force:
        print(f"Track '{track_id}' already exists in the index. Use --force to re-ingest.")
        idx.close()
        return

    print(f"Ingesting: {video_path}")
    print(f"  track_id = {track_id}")
    print(f"  title    = {title}")

    with tempfile.TemporaryDirectory() as tmp_dir:
        wav_path = os.path.join(tmp_dir, f"{track_id}.wav")

        print("Extracting audio...")
        extract_audio(video_path, wav_path)

        print("Fingerprinting...")
        hashes = fingerprint(wav_path)
        print(f"  Generated {len(hashes)} hashes")

        if idx.track_exists(track_id) and force:
            print("Force re-ingest: removing old fingerprints first...")
            idx.conn.execute("DELETE FROM fingerprints WHERE track_id = ?", (track_id,))
            idx.conn.execute("DELETE FROM tracks WHERE track_id = ?", (track_id,))
            idx.conn.commit()

        idx.add_track(track_id, hashes, title=title)

    print(f"Done. Index now has {len(idx)} unique hashes total.")
    idx.close()


def main():
    parser = argparse.ArgumentParser(description="Ingest a movie file into the fingerprint database.")
    parser.add_argument("video_path", help="Path to the movie/video file")
    parser.add_argument("--title", help="Human-readable movie title (optional)")
    parser.add_argument("--track-id", help="Custom track ID (optional, derived from filename if omitted)")
    parser.add_argument("--db", default=os.environ.get("DATABASE_URL"), help="Postgres connection string")
    parser.add_argument("--force", action="store_true", help="Re-ingest even if track_id already exists")

    args = parser.parse_args()
    ingest(args.video_path, title=args.title, track_id=args.track_id, db_path=args.db, force=args.force)


if __name__ == "__main__":
    main()