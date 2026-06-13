"""Shared narration pipeline for single-voice flows: AI Voiceover, Reddit, Twitter.

Flow: text (one or more segments) -> Fish Audio TTS (single voice) -> concat ->
word-level centered subtitles -> ffmpeg assembly over a background loop.
Optional static image overlays (e.g. a Reddit post card or tweet card) timed per segment.
"""
import os
import json
from sqlmodel import Session
from .config import settings
from .models import RenderJob, Project
from .providers import tts as tts_p
from .providers import subtitles as sub_p
from .providers import assemble as asm_p


def _update(session: Session, job: RenderJob, status: str, progress: int):
    job.status = status
    job.progress = progress
    session.add(job)
    session.commit()
    session.refresh(job)


async def run_narration_job(session: Session, job_id: int):
    """Generic single-voice narration render.

    project.data expects:
      voice_id: str (Fish Audio)
      segments: [{text, image_path?}]   # image_path optional top-card overlay
      background_path, subtitle_style, subtitle_settings, music_path, music_volume
    """
    job = session.get(RenderJob, job_id)
    project = session.get(Project, job.project_id)
    data = json.loads(project.data_json or "{}")
    work = os.path.join(settings.renders_dir, f"job_{job_id}")
    os.makedirs(work, exist_ok=True)

    try:
        voice_id = data.get("voice_id") or settings.fish_voice_a
        segments = data.get("segments", [])
        if not segments and data.get("text"):
            segments = [{"text": data["text"]}]

        # 1. TTS per segment
        _update(session, job, "tts", 30)
        audio_paths, durations = [], []
        for i, seg in enumerate(segments):
            ap = os.path.join(work, f"seg_{i}.mp3")
            await tts_p.synthesize(seg["text"], voice_id, ap)
            audio_paths.append(ap)
            durations.append(asm_p.get_duration(ap))

        voice_path = os.path.join(work, "voice.mp3")
        asm_p.concat_audio(audio_paths, voice_path)

        # 2. Optional top-card image overlays timed per segment
        overlays, t = [], 0.0
        for i, seg in enumerate(segments):
            if seg.get("image_path"):
                overlays.append({"path": seg["image_path"], "start": t, "end": t + durations[i]})
            t += durations[i]

        # 3. Subtitles (centered karaoke)
        _update(session, job, "subtitles", 65)
        words = sub_p.transcribe_words(voice_path)
        ass_path = os.path.join(work, "subs.ass")
        sub_p.write_ass(words, ass_path, style=data.get("subtitle_style", "Default"),
                        settings=data.get("subtitle_settings", {}))

        # 4. Assembly
        _update(session, job, "assembling", 90)
        out_path = os.path.join(settings.renders_dir, f"render_{job_id}.mp4")
        asm_p.assemble(data.get("background_path"), voice_path, ass_path, out_path,
                       broll_overlays=overlays,
                       music_path=data.get("music_path"),
                       music_volume=data.get("music_volume", 0.2))
        job.output_path = out_path
        _update(session, job, "ready", 100)
    except Exception as e:  # noqa: BLE001
        job.error = str(e)
        _update(session, job, "error", job.progress)
