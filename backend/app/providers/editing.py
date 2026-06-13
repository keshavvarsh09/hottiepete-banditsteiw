"""ffmpeg helpers for AI Captions (burn subs onto an uploaded video) and Split Video."""
import subprocess

W, H = 1080, 1920


def burn_captions(video_path: str, ass_path: str, out_path: str):
    """Scale/crop an uploaded video to 9:16 and burn centered captions onto it."""
    ass_escaped = ass_path.replace("\\", "/").replace(":", "\\:")
    fc = (
        f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,"
        f"crop={W}:{H},setsar=1[base];[base]ass='{ass_escaped}'[vout]"
    )
    cmd = ["ffmpeg", "-y", "-i", video_path,
           "-filter_complex", fc,
           "-map", "[vout]", "-map", "0:a?",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", out_path]
    subprocess.run(cmd, check=True, capture_output=True)
    return out_path


def split_stack(main_path, bg_path, out_path, ass_path=None,
                main_speed=1.0, bg_speed=1.0):
    """Brain-rot split layout: main clip on top half, background clip on bottom half.

    Each half is 1080x960. Optional captions burned over the whole frame.
    """
    half = H // 2
    fc = [
        f"[0:v]setpts={1.0/main_speed}*PTS,scale={W}:{half}:force_original_aspect_ratio=increase,"
        f"crop={W}:{half},setsar=1[top]",
        f"[1:v]setpts={1.0/bg_speed}*PTS,scale={W}:{half}:force_original_aspect_ratio=increase,"
        f"crop={W}:{half},setsar=1[bot]",
        "[top][bot]vstack=inputs=2[stacked]",
    ]
    last = "stacked"
    if ass_path:
        ass_escaped = ass_path.replace("\\", "/").replace(":", "\\:")
        fc.append(f"[stacked]ass='{ass_escaped}'[vout]")
        last = "vout"
    cmd = ["ffmpeg", "-y", "-i", main_path, "-i", bg_path,
           "-filter_complex", ";".join(fc),
           "-map", f"[{last}]", "-map", "0:a?",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
           "-shortest", out_path]
    subprocess.run(cmd, check=True, capture_output=True)
    return out_path
