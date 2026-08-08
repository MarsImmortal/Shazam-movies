import sys
sys.path.append("src")

from fingerprint import fingerprint
from index import FingerprintIndex
from match import identify

# fresh DB file
idx = FingerprintIndex("data/fingerprints.db")

if not idx.track_exists("test1"):
    idx.add_track("test1", fingerprint("data/audio/test1.wav"), title="Night of the Living Dead (clip)")
if not idx.track_exists("test2"):
    idx.add_track("test2", fingerprint("data/audio/test2.wav"), title="Test2 clip")

print(f"Index size: {len(idx)} unique hashes")

result = identify("data/audio/query1_noisy.wav", idx, fingerprint)
print("Query from test1 clip ->", result)

result2 = identify("data/audio/query2.wav", idx, fingerprint)
print("Query from test2 clip ->", result2)

idx.close()