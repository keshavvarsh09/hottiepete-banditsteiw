"""ffmpeg assembly: background loop -> B-roll top overlay -> character cutouts -> centered captions -> mixed audio. Output 1080x1920."""
import subprocess
import os

W, H = 1080, 1920


def concat_audio(audio_paths, out_path, gap_ms: int = 250):
    """Concatenate per-line mp3s with small silence gaps."""
    parts = "|".join(audio_paths)
    # simple concat; gaps handled by appending short silence files upstream if needed
    cmd = [
        "ffmpeg", "-y", "-i", f"concat:{parts}",
        "-acodec", "libmp3lame", out_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return out_path


def get_duration(path: str) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        check=True, capture_output=True, text=True,
    )
    return float(out.stdout.strip())


def assemble(background_path, voice_path, ass_path, out_path,
             broll_overlays=None, character_overlays=None, music_path=None, music_volume=0.2):
    """Compose the final 9:16 video.

    broll_overlays: list of {path, start, end} drawn in the TOP region.
    character_overlays: list of {path, x, y, scale} static cutouts.
    """
    broll_overlays = broll_overlays or []
    character_overlays = character_overlays or []
    duration = get_duration(voice_path)

    inputs = ["-stream_loop", "-1", "-i", background_path, "-i", voice_path]
    for ov in broll_overlays:
        inputs += ["-i", ov["path"]]
    for ch in character_overlays:
        inputs += ["-i", ch["path"]]
    if music_path:
        inputs += ["-stream_loop", "-1", "-i", music_path]

    # base: scale+crop background to 1080x1920
    fc = [f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1[base]"]
    last = "base"
    idx = 2  # video input index after bg(0) and voice(1)

    # B-roll overlays in the top region (e.g. y=120, width ~ 900 centered)
    for ov in broll_overlays:
        fc.append(f"[{idx}:v]scale=900:-1[br{idx}]")
        fc.append(
            f"[{last}][br{idx}]overlay=(W-w)/2:160:enable='between(t,{ov['start']},{ov['end']})'[v{idx}]"
        )
        last = f"v{idx}"
        idx += 1

    # character cutouts (positioned, scaled)
    for ch in character_overlays:
        scale = ch.get("scale", 1.0)
        fc.append(f"[{idx}:v]scale=iw*{scale}:-1[ch{idx}]")
        fc.append(f"[{last}][ch{idx}]overlay={int(ch.get('x',0))}:{int(ch.get('y',0))}[v{idx}]")
        last = f"v{idx}"
        idx += 1

    # burn centered captions
    ass_escaped = ass_path.replace("\\", "/").replace(":", "\\:")
    fc.append(f"[{last}]ass='{ass_escaped}'[vout]")

    # audio mix
    if music_path:
        music_idx = idx
        fc.append(f"[{music_idx}:a]volume={music_volume}[bg_a]")
        fc.append("[1:a][bg_a]amix=inputs=2:duration=first[aout]")
        amap = "[aout]"
    else:
        amap = "1:a"

    cmd = ["ffmpeg", "-y", *inputs,
           "-filter_complex", ";".join(fc),
           "-map", "[vout]", "-map", amap,
           "-t", str(duration),
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
           "-shortest", out_path]
    subprocess.run(cmd, check=True, capture_output=True)
    return out_path
