from collections import Counter


def find_matches(query_hashes, index):
    """Batch-lookup all query hashes at once, return (track_id, db_time, query_time) tuples."""
    hash_list = [h for h, _ in query_hashes]
    lookup_map = index.lookup_batch(hash_list)

    matches = []
    for h, query_t in query_hashes:
        for track_id, db_t in lookup_map.get(h, []):
            matches.append((track_id, db_t, query_t))
    return matches


def score_matches(matches):
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
    query_hashes = fingerprint_fn(query_wav_path)
    matches = find_matches(query_hashes, index)
    results = score_matches(matches)

    if not results or results[0][2] < min_score:
        return None

    track_id, offset, score = results[0]
    return {"track_id": track_id, "offset_frames": offset, "score": score}