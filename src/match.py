from collections import Counter


def find_matches(query_hashes, index):
    """Look up query hashes in index, return (track_id, db_time, query_time) tuples."""
    matches = []
    for h, query_t in query_hashes:
        for track_id, db_t in index.lookup(h):
            matches.append((track_id, db_t, query_t))
    return matches


def score_matches(matches):
    """
    Group matches by track_id, compute offset histogram per track,
    return best (track_id, offset, score) sorted by score descending.
    """
    by_track = {}
    for track_id, db_t, query_t in matches:
        by_track.setdefault(track_id, []).append(db_t - query_t)

    results = []
    for track_id, offsets in by_track.items():
        counts = Counter(offsets)
        best_offset, best_score = counts.most_common(1)[0]
        results.append((track_id, best_offset, best_score))

    results.sort(key=lambda x: x[2], reverse=True)
    return results


def identify(query_wav_path, index, fingerprint_fn, min_score=50):
    """End-to-end: fingerprint a query clip, match against index, return best guess."""
    query_hashes = fingerprint_fn(query_wav_path)
    matches = find_matches(query_hashes, index)
    results = score_matches(matches)

    if not results or results[0][2] < min_score:
        return None  # no confident match

    track_id, offset, score = results[0]
    return {"track_id": track_id, "offset_frames": offset, "score": score}
