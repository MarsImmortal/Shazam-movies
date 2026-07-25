from collections import defaultdict
import pickle
import os


class FingerprintIndex:
    def __init__(self):
        self.index = defaultdict(list)  # hash -> [(track_id, offset_time), ...]

    def add_track(self, track_id, hashes):
        for h, t in hashes:
            self.index[h].append((track_id, t))

    def lookup(self, h):
        return self.index.get(h, [])

    def save(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
        with open(path, "wb") as f:
            pickle.dump(dict(self.index), f)

    def load(self, path):
        with open(path, "rb") as f:
            self.index = defaultdict(list, pickle.load(f))
        return self

    def __len__(self):
        return len(self.index)