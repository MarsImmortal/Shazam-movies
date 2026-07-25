import sys
sys.path.append("src")

from fingerprint import fingerprint
from index import FingerprintIndex
from match import identify

idx = FingerprintIndex()
idx.add_track("test1", fingerprint("data/audio/test1.wav"))

result = identify("data/audio/query1_noisy.wav", idx, fingerprint)
print(result)