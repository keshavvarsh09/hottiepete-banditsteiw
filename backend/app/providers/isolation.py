"""Voice isolation: separate vocals from background music/noise using Demucs.

Demucs is a local model (no API key). It writes separated stems; we keep the
vocals stem. ffmpeg first extracts audio from video inputs.
"""
import os
import subprocess
import glob


def _extract_audio(input_path: str, out_wav: str) -> str:
    subprocess.run(
        ["ffmpeg", "-y", "-i", input_path, "-vn", "-ac", "2", "-ar", "44100", out_wav],
        check=True, capture_output=True,
    )
    return out_wav


def isolate_vocals(input_path: str, work_dir: str) -> str:
    """Return the path to an isolated-vocals wav."""
    os.makedirs(work_dir, exist_ok=True)
    src_wav = os.path.join(work_dir, "input.wav")
    _extract_audio(input_path, src_wav)

    # Demucs two-stem mode: vocals vs. the rest.
    subprocess.run(
        ["python", "-m", "demucs", "--two-stems=vocals", "-o", work_dir, src_wav],
        check=True, capture_output=True,
    )
    matches = glob.glob(os.path.join(work_dir, "**", "vocals.wav"), recursive=True)
    if not matches:
        raise RuntimeError("Demucs did not produce a vocals stem")
    return matches[0]
