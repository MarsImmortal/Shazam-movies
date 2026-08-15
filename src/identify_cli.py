import argparse
import sys
import os

sys.path.append(os.path.dirname(__file__))

from fingerprint import fingerprint
from index import FingerprintIndex
from match import identify


def main():
    parser = argparse.ArgumentParser(description="Identify a movie from an audio/video clip.")
    parser.add_argument("clip_path", help="Path to the query clip (wav or video)")
    parser.add_argument("--db", default="data/fingerprints.db")
    parser.add_argument("--min-score", type=int, default=50)

    args = parser.parse_args()

    idx = FingerprintIndex(args.db)
    result = identify(args.clip_path, idx, fingerprint, min_score=args.min_score)
    idx.close()

    if result:
        print(f"Match found: {result['track_id']}  (score={result['score']}, offset={result['offset_frames']} frames)")
    else:
        print("No confident match found.")


if __name__ == "__main__":
    main()