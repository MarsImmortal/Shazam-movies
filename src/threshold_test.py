import sys
sys.path.append("src")

from fingerprint import fingerprint
from index import FingerprintIndex
from match import find_matches, score_matches

# Build your existing multi-track index
idx = FingerprintIndex()
idx.add_track("test1", fingerprint("data/audio/test1.wav"))
idx.add_track("test2", fingerprint("data/audio/test2.wav"))

def get_top_score(wav_path, idx):
    hashes = fingerprint(wav_path)
    matches = find_matches(hashes, idx)
    results = score_matches(matches)
    if not results:
        return 0, None
    track_id, offset, score = results[0]
    return score, track_id

# --- Negative (unrelated) queries - should score LOW ---
negatives = ["data/audio/negative1.wav", "data/audio/negative2.wav", "data/audio/negative3.wav"]

print("=== NEGATIVE (unrelated) queries ===")
neg_scores = []
for path in negatives:
    score, track_id = get_top_score(path, idx)
    neg_scores.append(score)
    print(f"{path:35s} -> top_score={score:4d}  (falsely matched: {track_id})")

# --- Positive (real) queries - should score HIGH ---
positives = ["data/audio/query1.wav", "data/audio/query1_noisy.wav", "data/audio/query2.wav"]

print("\n=== POSITIVE (real) queries ===")
pos_scores = []
for path in positives:
    score, track_id = get_top_score(path, idx)
    pos_scores.append(score)
    print(f"{path:35s} -> top_score={score:4d}  (matched: {track_id})")

print(f"\nMax negative score: {max(neg_scores)}")
print(f"Min positive score: {min(pos_scores)}")
print(f"Suggested threshold (midpoint): {(max(neg_scores) + min(pos_scores))//2}")
