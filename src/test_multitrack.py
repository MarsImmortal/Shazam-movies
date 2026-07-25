import sys
sys.path.append("src")

from fingerprint import fingerprint
from index import FingerprintIndex
from match import identify

idx = FingerprintIndex()
idx.add_track("test1", fingerprint("data/audio/test1.wav"))
idx.add_track("test2", fingerprint("data/audio/test2.wav"))

print(f"Index size: {len(idx)} unique hashes")

# Query with a clip from test1 - should match test1, NOT test2
result = identify("data/audio/query1_noisy.wav", idx, fingerprint)
print("Query from test1 clip ->", result)

result2 = identify("data/audio/query2.wav", idx, fingerprint)
print("Query from test2 clip ->", result2)