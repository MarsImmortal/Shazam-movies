import librosa
import numpy as np
from scipy.ndimage import maximum_filter

# Locked-in parameters from validation phase
DEFAULT_PARAMS = {
    "sr": 8000,
    "n_fft": 2048,
    "hop_length": 512,
    "neighborhood_size": 20,
    "threshold": -50,
    "fan_out": 10,
    "min_dt": 1,
    "max_dt": 100,
    "max_freq_dist": 200,
}


def compute_spectrogram(wav_path, sr, n_fft, hop_length):
    y, _ = librosa.load(wav_path, sr=sr)
    S = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop_length))
    return librosa.amplitude_to_db(S, ref=np.max)


def find_peaks(S_db, neighborhood_size, threshold):
    local_max = maximum_filter(S_db, size=neighborhood_size) == S_db
    peaks_mask = local_max & (S_db > threshold)
    freq_idx, time_idx = np.where(peaks_mask)
    peaks = list(zip(time_idx, freq_idx))
    peaks.sort(key=lambda p: p[0])
    return peaks


def hash_pack(f1, f2, dt):
    f1 = f1 & 0x3FF
    f2 = f2 & 0x3FF
    dt = dt & 0xFFF
    return (f1 << 22) | (f2 << 12) | dt


def hash_unpack(h):
    dt = h & 0xFFF
    f2 = (h >> 12) & 0x3FF
    f1 = (h >> 22) & 0x3FF
    return f1, f2, dt


def generate_hashes(peaks, fan_out, min_dt, max_dt, max_freq_dist):
    hashes = []
    n = len(peaks)
    for i in range(n):
        t1, f1 = peaks[i]
        count = 0
        for j in range(i + 1, n):
            t2, f2 = peaks[j]
            dt = t2 - t1
            if dt < min_dt:
                continue
            if dt > max_dt:
                break
            if abs(f2 - f1) > max_freq_dist:
                continue
            hashes.append((hash_pack(f1, f2, dt), t1))
            count += 1
            if count >= fan_out:
                break
    return hashes


def fingerprint(wav_path, params=None):
    """Full pipeline: wav -> list of (hash, anchor_time_offset)."""
    p = {**DEFAULT_PARAMS, **(params or {})}
    S_db = compute_spectrogram(wav_path, p["sr"], p["n_fft"], p["hop_length"])
    peaks = find_peaks(S_db, p["neighborhood_size"], p["threshold"])
    hashes = generate_hashes(
        peaks, p["fan_out"], p["min_dt"], p["max_dt"], p["max_freq_dist"]
    )
    return hashes


if __name__ == "__main__":
    import sys
    result = fingerprint(sys.argv[1])
    print(f"Generated {len(result)} hashes")