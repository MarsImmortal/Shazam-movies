import subprocess
import os

def extract_audio(video_path, output_path, sr=8000):
    """Extract mono audio at given sample rate from a video file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vn", "-ac", "1", "-ar", str(sr),
        "-acodec", "pcm_s16le", output_path
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


if __name__ == "__main__":
    import sys
    extract_audio(sys.argv[1], sys.argv[2])