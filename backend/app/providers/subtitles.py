"""Word-level karaoke subtitles via faster-whisper, written as an ASS file.

Centered. Style presets and settings are applied at burn-in time by ffmpeg.
"""
from faster_whisper import WhisperModel

_model = None


def _get_model():
    global _model
    if _model is None:
        _model = WhisperModel("base", device="cpu", compute_type="int8")
    return _model


def transcribe_words(audio_path: str):
    """Return a list of {word, start, end} with word-level timestamps."""
    model = _get_model()
    segments, _ = model.transcribe(audio_path, word_timestamps=True)
    words = []
    for seg in segments:
        for w in seg.words or []:
            words.append({"word": w.word.strip(), "start": w.start, "end": w.end})
    return words


def _ts(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"


PRESETS = {
    "Default": {"font": "Arial", "size": 80, "primary": "&H00FFFFFF", "outline": 4, "shadow": 1},
    "TikTok": {"font": "Arial Black", "size": 90, "primary": "&H00FFFFFF", "outline": 6, "shadow": 0},
    "Cinema": {"font": "Georgia", "size": 72, "primary": "&H00F0F0F0", "outline": 2, "shadow": 2},
    "Bold": {"font": "Impact", "size": 96, "primary": "&H00FFFFFF", "outline": 6, "shadow": 1},
    "Colorful": {"font": "Arial Black", "size": 88, "primary": "&H0000FFFF", "outline": 5, "shadow": 1},
    "Cyberpunk": {"font": "Consolas", "size": 84, "primary": "&H00FF00FF", "outline": 5, "shadow": 0},
    "Soft": {"font": "Verdana", "size": 76, "primary": "&H00FFFFFF", "outline": 2, "shadow": 3},
    "Cartoon": {"font": "Comic Sans MS", "size": 86, "primary": "&H0000E0FF", "outline": 5, "shadow": 1},
    "Haze": {"font": "Arial", "size": 80, "primary": "&H00FFFFFF", "outline": 1, "shadow": 4},
}


def write_ass(words, out_path: str, style: str = "Default", settings: dict | None = None,
              video_w: int = 1080, video_h: int = 1920):
    """Write a centered karaoke .ass subtitle file (one word highlighted at a time)."""
    settings = settings or {}
    p = dict(PRESETS.get(style, PRESETS["Default"]))
    p.update({k: settings[k] for k in ("font", "size", "outline", "shadow", "primary") if k in settings})

    # Vertical position: centered by default; allow override via settings['vertical_position']
    margin_v = settings.get("vertical_position", video_h // 2 - p["size"])
    transform = settings.get("text_transform")

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {video_w}
PlayResY: {video_h}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Outline, Shadow, Alignment, MarginL, MarginR, MarginV
Style: Main,{p['font']},{p['size']},{p['primary']},&H00000000,&H64000000,-1,{p['outline']},{p['shadow']},5,40,40,{margin_v}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    for w in words:
        text = w["word"]
        if transform == "uppercase":
            text = text.upper()
        lines.append(
            f"Dialogue: 0,{_ts(w['start'])},{_ts(w['end'])},Main,,0,0,0,,{text}"
        )
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(lines) + "\n")
    return out_path
